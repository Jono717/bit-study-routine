#!/usr/bin/env python3
"""Keep the portfolio's references in Zotero, through the Zotero Web API.

    status                      check the API key and show the library and collection
    push FILE.json [--dry-run]  add CSL JSON items (e.g. references/zotero_seed_*.json) to the collection,
                                skipping any whose citation key or title is already there
    pull                        write the collection as CSL JSON to Workings/references/zotero_library.json,
                                the file render_portfolio.py formats citations from

Options: --collection NAME (default BIT), --out FILE (pull).

Needs network access to api.zotero.org and an API key with library and write access, stored in the
macOS Keychain (`security add-generic-password -a "$USER" -s zotero-api-key -w`) or in the
ZOTERO_API_KEY environment variable. Set ZOTERO_KEYCHAIN_ACCOUNT if you stored the key under a
different Keychain account name. The key is never printed. Zotero desktop picks the changes up on
its next sync.

Every item carries "Citation Key: <key>" in its Extra field; that is how the markdown's [@key] finds it.

Usage:
    uv run python zotero_sync.py status
    uv run python zotero_sync.py push ../../../../Workings/references/zotero_seed.json
    uv run python zotero_sync.py pull
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.zotero.org"
WORKINGS = pathlib.Path(__file__).resolve().parents[4] / "Workings"
DEFAULT_OUT = WORKINGS / "references" / "zotero_library.json"

# CSL type -> (Zotero item type, {CSL variable: Zotero field}); anything unmapped goes to Extra as
# "variable: value", which Zotero turns back into the CSL variable on export.
TYPES = {
    "book": ("book", {"publisher": "publisher", "publisher-place": "place", "edition": "edition", "URL": "url", "ISBN": "ISBN"}),
    "chapter": ("bookSection", {"container-title": "bookTitle", "volume": "volume", "page": "pages", "publisher": "publisher",
                                "publisher-place": "place", "URL": "url"}),
    "paper-conference": ("conferencePaper", {"container-title": "proceedingsTitle", "event-title": "conferenceName",
                                             "volume": "volume", "page": "pages", "publisher": "publisher", "DOI": "DOI", "URL": "url"}),
    "article-journal": ("journalArticle", {"container-title": "publicationTitle", "volume": "volume", "issue": "issue",
                                           "page": "pages", "DOI": "DOI", "URL": "url"}),
    "article-magazine": ("magazineArticle", {"container-title": "publicationTitle", "volume": "volume", "issue": "issue",
                                             "page": "pages", "URL": "url"}),
    "report": ("report", {"publisher": "institution", "publisher-place": "place", "number": "reportNumber",
                          "genre": "reportType", "URL": "url"}),
    "webpage": ("webpage", {"container-title": "websiteTitle", "URL": "url"}),
    "speech": ("presentation", {"genre": "presentationType", "event-title": "meetingName", "event-place": "place", "URL": "url"}),
    "manuscript": ("manuscript", {"genre": "manuscriptType", "publisher-place": "place", "URL": "url"}),
    "legislation": ("statute", {"number": "publicLawNumber", "URL": "url"}),
}
SKIP = {"id", "type", "title", "author", "editor", "issued", "accessed", "note", "citation-key"}
# CSL variables whose Zotero field has the same meaning on any item type that has it (per the live schema)
GENERIC = {"original-date": "originalDate", "DOI": "DOI", "ISBN": "ISBN", "URL": "url", "publisher": "publisher",
           "publisher-place": "place", "volume": "volume", "issue": "issue", "page": "pages", "edition": "edition"}
SCHEMA_CACHE = pathlib.Path.home() / "Library/Caches/bit-docx/zotero/schema.json"


def schema():
    """Zotero's item schema (types, valid fields, creator roles), cached; refreshed when reachable."""
    try:
        with urllib.request.urlopen(API + "/schema", timeout=30) as resp:
            data = json.loads(resp.read())
        SCHEMA_CACHE.parent.mkdir(parents=True, exist_ok=True)
        SCHEMA_CACHE.write_text(json.dumps(data))
    except (urllib.error.URLError, TimeoutError):
        if not SCHEMA_CACHE.exists():
            sys.exit("Cannot reach api.zotero.org/schema and no cached copy")
        data = json.loads(SCHEMA_CACHE.read_text())
    return {t["itemType"]: {"fields": {f["field"] for f in t["fields"]},
                            "primary": next((c["creatorType"] for c in t.get("creatorTypes", []) if c.get("primary")), "author"),
                            "roles": {c["creatorType"] for c in t.get("creatorTypes", [])}}
            for t in data["itemTypes"]}


def api_key():
    if key := os.environ.get("ZOTERO_API_KEY"):
        return key.strip()
    account = os.environ.get("ZOTERO_KEYCHAIN_ACCOUNT") or os.environ.get("USER", "")
    r = subprocess.run(["security", "find-generic-password", "-a", account, "-s", "zotero-api-key", "-w"],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("No Zotero API key: set ZOTERO_API_KEY, or store it with "
                 "`security add-generic-password -a \"$USER\" -s zotero-api-key -w`")
    return r.stdout.strip()


def call(method, path, key, body=None, params=None, headers=None):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Zotero-API-Key": key, "Zotero-API-Version": "3", "Content-Type": "application/json",
                                          **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read() or "null"), resp.headers
    except urllib.error.HTTPError as err:
        sys.exit(f"Zotero API {method} {path}: HTTP {err.code} {err.read()[:300]!r}")
    except urllib.error.URLError as err:
        sys.exit(f"Zotero API unreachable ({err.reason}); is api.zotero.org reachable from this machine?")


def paged(path, key, params):
    start, out = 0, []
    while True:
        data, headers = call("GET", path, key, params={**params, "limit": 100, "start": start})
        batch = data["items"] if isinstance(data, dict) and "items" in data else data
        out += batch
        start += len(batch)
        if not batch or start >= int(headers.get("Total-Results", start)):
            return out


def library(key):
    me, _ = call("GET", "/keys/current", key)
    return f"/users/{me['userID']}", me


def collection_key(prefix, key, name, create=False):
    for c in paged(f"{prefix}/collections", key, {}):
        if c["data"]["name"] == name:
            return c["key"]
    if not create:
        sys.exit(f"No collection named {name!r} in the Zotero library")
    data, _ = call("POST", f"{prefix}/collections", key, body=[{"name": name}])
    return data["successful"]["0"]["key"]


def citation_key(extra):
    m = re.search(r"^Citation Key:\s*(\S+)", extra or "", re.M)
    return m.group(1) if m else None


def date(parts):
    p = (parts or {}).get("date-parts", [[]])[0]
    return "-".join(f"{v:02d}" if i else str(v) for i, v in enumerate(p))


def to_zotero(item, collection, types):
    """CSL JSON item to a Zotero API item, using only fields and creator roles valid for its type."""
    item_type, fields = TYPES[item["type"]]
    valid = types[item_type]
    z = {"itemType": item_type, "title": item["title"], "collections": [collection], "tags": [{"tag": "BIT"}]}
    if item_type == "statute":
        z["nameOfAct"] = z.pop("title")
    role_of = {"author": valid["primary"], "editor": "editor" if "editor" in valid["roles"] else "contributor"}
    z["creators"] = [({"name": n["literal"]} if "literal" in n else {"lastName": n["family"], "firstName": n.get("given", "")})
                     | {"creatorType": role_of[role]} for role in ("author", "editor") for n in item.get(role, [])]
    if "issued" in item:
        z["dateEnacted" if item_type == "statute" else "date"] = date(item["issued"])
    if "accessed" in item:
        z["accessDate"] = date(item["accessed"])
    extra = [line for line in item.get("note", "").splitlines() if line.strip()]
    for var, value in item.items():
        if var in SKIP:
            continue
        field = fields.get(var) or GENERIC.get(var)
        if field in valid["fields"]:
            z[field] = date(value) if isinstance(value, dict) else value
        else:
            extra.append(f"{var}: {date(value) if isinstance(value, dict) else value}")
    if "BIT check" in item.get("note", ""):
        z["tags"].append({"tag": "bit-check"})
    z["extra"] = "\n".join(extra)
    return z


def push(path, dry_run=False, collection_name="BIT"):
    items = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    types = schema()
    if dry_run:
        print(json.dumps([to_zotero(i, "COLLECTIONKEY", types) for i in items], ensure_ascii=False, indent=1))
        return
    key = api_key()
    prefix, _ = library(key)
    ck = collection_key(prefix, key, collection_name, create=True)
    have = paged(f"{prefix}/collections/{ck}/items", key, {"format": "json"})
    keys = {citation_key(i["data"].get("extra")) for i in have}
    titles = {(i["data"].get("title") or i["data"].get("nameOfAct") or "").lower() for i in have}
    new = [i for i in items if (i.get("citation-key") or i["id"]) not in keys and i["title"].lower() not in titles]
    for n in range(0, len(new), 50):
        data, _ = call("POST", f"{prefix}/items", key, body=[to_zotero(i, ck, types) for i in new[n:n + 50]])
        for idx, err in (data.get("failed") or {}).items():
            print(f"failed: {new[n + int(idx)]['id']}: {err.get('message')}")
    print(f"added {len(new)} item(s) to {collection_name!r}; {len(items) - len(new)} already there")


def update(citation, fields=None, extra=None, drop_tags=(), collection_name="BIT"):
    """Patch one item, found by its citation key: Zotero fields, a replacement Extra, tags to remove.

    Uses the item's version so a change made meanwhile in Zotero desktop is never overwritten (HTTP 412).
    """
    key = api_key()
    prefix, _ = library(key)
    ck = collection_key(prefix, key, collection_name)
    item = next((i for i in paged(f"{prefix}/collections/{ck}/items/top", key, {"format": "json"})
                 if citation_key(i["data"].get("extra")) == citation), None)
    if item is None:
        sys.exit(f"No item with Citation Key {citation!r} in {collection_name!r}")
    body = dict(fields or {})
    if extra is not None:
        body["extra"] = extra
    if drop_tags:
        body["tags"] = [t for t in item["data"]["tags"] if t["tag"] not in drop_tags]
    call("PATCH", f"{prefix}/items/{item['key']}", key, body=body,
         headers={"If-Unmodified-Since-Version": str(item["version"])})
    return item["data"]


def pull(out=DEFAULT_OUT, collection_name="BIT"):
    key = api_key()
    prefix, _ = library(key)
    ck = collection_key(prefix, key, collection_name)
    raw = paged(f"{prefix}/collections/{ck}/items/top", key, {"format": "json"})
    keys = {i["key"]: citation_key(i["data"].get("extra")) for i in raw}
    csl = paged(f"{prefix}/collections/{ck}/items/top", key, {"format": "csljson"})
    missing = []
    for item in csl:
        zkey = str(item["id"]).split("/")[-1]
        if keys.get(zkey):
            item["citation-key"] = keys[zkey]
        else:
            missing.append(item.get("title", zkey))
    pathlib.Path(out).write_text(json.dumps(csl, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {len(csl)} item(s) to {out}")
    if missing:
        print(f"{len(missing)} item(s) have no 'Citation Key:' line in Extra and cannot be cited yet: " + "; ".join(missing[:10]))


if __name__ == "__main__":
    argv = sys.argv[1:]
    opt = lambda name, default: next((argv[k + 1] for k, a in enumerate(argv) if a == name), default)
    args = [a for k, a in enumerate(argv) if not a.startswith("--") and (k == 0 or argv[k - 1] not in ("--collection", "--out"))]
    name = opt("--collection", "BIT")
    if args[:1] == ["status"]:
        prefix, me = library(api_key())
        print(f"key OK for {me.get('username')} ({prefix}); access: {json.dumps(me.get('access', {}).get('user', {}))}")
        print(f"collection {name!r}: {collection_key(prefix, api_key(), name)}")
    elif args[:1] == ["push"] and len(args) == 2:
        push(args[1], dry_run="--dry-run" in argv, collection_name=name)
    elif args[:1] == ["pull"]:
        pull(opt("--out", DEFAULT_OUT), collection_name=name)
    else:
        print(__doc__)
        sys.exit(1)

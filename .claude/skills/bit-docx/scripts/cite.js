#!/usr/bin/env node
// Format citations and a bibliography with Zotero's own citeproc-js and APA style.
//
// Reads JSON on stdin:
//   { citeproc, style, locale,          paths to citeproc.js, the .csl style and locales-xx-XX.xml
//     items: [CSL-JSON item, ...],
//     clusters: [[{id, locator, label, prefix, suffix, "suppress-author", "author-only"}, ...], ...] }
// Writes JSON on stdout:
//   { clusters: [html, ...], bibliography: [{ids: [...], html}], errors: [...] }
//
// Called by render_portfolio.py; the engine files are extracted from the installed Zotero app, so the
// output matches what Zotero's Word plugin would produce.
"use strict";
const fs = require("fs");
const vm = require("vm");

const input = JSON.parse(fs.readFileSync(0, "utf8"));
const context = { console };
vm.createContext(context);
vm.runInContext(fs.readFileSync(input.citeproc, "utf8") + "\n;globalThis.CSL = CSL;", context);
const CSL = context.CSL;

const byId = Object.fromEntries(input.items.map((item) => [item.id, item]));
const errors = [];
const sys = {
  retrieveLocale: () => fs.readFileSync(input.locale, "utf8"),
  retrieveItem: (id) => byId[id],
};
const engine = new CSL.Engine(sys, fs.readFileSync(input.style, "utf8"), "en-US", true);
engine.setOutputFormat("html");

const cited = [...new Set(input.clusters.flat().map((c) => c.id))].filter((id) => {
  if (!byId[id]) errors.push(`unknown citation key: ${id}`);
  return Boolean(byId[id]);
});
engine.updateItems(cited);

const clusters = input.clusters.map((cluster) => {
  const known = cluster.filter((c) => byId[c.id]);
  if (!known.length) return null;
  try {
    return engine.makeCitationCluster(known);
  } catch (err) {
    errors.push(`cluster ${known.map((c) => c.id).join(";")}: ${err.message}`);
    return null;
  }
});

let bibliography = [];
if (cited.length) {
  const [params, entries] = engine.makeBibliography();
  bibliography = entries.map((html, i) => ({ ids: params.entry_ids[i], html: html.trim() }));
}
process.stdout.write(JSON.stringify({ clusters, bibliography, errors }));

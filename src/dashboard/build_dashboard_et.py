#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build output/dashboard_et.html (the Estonian dashboard) from its editable
source files:
  - src/dashboard/template_et.html    ({{dot.path}} placeholders for UI chrome)
  - src/dashboard/app_et.js           ("@@dot.path@@" / @@OBJ:dot.path@@ placeholders)
  - src/dashboard/strings_et.json     (every editable Estonian UI string --
                                        edit THIS file, then re-run this script)
  - src/dashboard/methodology_body_et.html
  - output/dashboard_data_et.json     (translated data -- regenerate via
                                        build_et_data.py if the English data changes)

Run from the project root: python3 src/dashboard/build_dashboard_et.py
"""
import io, json, os, re

BASE = os.path.expanduser("~/mnt/toidujulgeolek")
DASH = f"{BASE}/src/dashboard"
OUT = f"{BASE}/output"

def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()

with io.open(f"{DASH}/strings_et.json", encoding="utf-8") as f:
    strings_nested = json.load(f)

# The lookup-table objects (js.data_status_map, js.sex_map, js.scen_label,
# js.delta_label, js.headers.*) must stay intact, not be flattened further.
LOOKUP_KEYS = {
    "js.data_status_map", "js.sex_map", "js.scen_label", "js.delta_label",
    "js.headers.ss_table", "js.headers.cons_table", "js.headers.faostat_table",
}

def flatten2(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and key not in LOOKUP_KEYS:
            out.update(flatten2(v, key))
        else:
            out[key] = v
    return out

flat = flatten2(strings_nested)

# ---------------------------------------------------------------------
# 1. template_et.html: {{dot.path}} -> plain text substitution
# ---------------------------------------------------------------------
template = read(f"{DASH}/template_et.html")
missing = []
for key, val in flat.items():
    token = "{{" + key + "}}"
    if token in template:
        if not isinstance(val, str):
            continue
        template = template.replace(token, val)
leftover = re.findall(r"\{\{[a-z0-9_.]+\}\}", template)
if leftover:
    print("WARNING: unresolved template placeholders:", leftover)

# ---------------------------------------------------------------------
# 2. app_et.js: "@@dot.path@@" (string) and @@OBJ:dot.path@@ (object/array)
# ---------------------------------------------------------------------
app_js = read(f"{DASH}/app_et.js")
for key, val in flat.items():
    str_token = '"@@' + key + '@@"'
    obj_token = "@@OBJ:" + key + "@@"
    if str_token in app_js:
        app_js = app_js.replace(str_token, json.dumps(val, ensure_ascii=False))
    if obj_token in app_js:
        app_js = app_js.replace(obj_token, json.dumps(val, ensure_ascii=False))
leftover_js = re.findall(r'"@@[a-z0-9_.]+@@"|@@OBJ:[a-z0-9_.]+@@', app_js)
if leftover_js:
    print("WARNING: unresolved app.js placeholders:", leftover_js)

# ---------------------------------------------------------------------
# 3. assemble dashboard_et.html the same way build_dashboard.py does
# ---------------------------------------------------------------------
with io.open(f"{OUT}/dashboard_data_et.json", encoding="utf-8") as f:
    data_raw = f.read()
    json.loads(data_raw)  # validate

meth_body = read(f"{DASH}/methodology_body_et.html")

out = template.replace("__DASHBOARD_DATA__", data_raw).replace("__APP_JS__", app_js)
placeholder = '<div class="appendix-body" id="meth-body"></div>'
assert placeholder in out, "meth-body placeholder not found in template_et.html"
out = out.replace(placeholder, '<div class="appendix-body" id="meth-body">' + meth_body + '</div>')

with io.open(f"{OUT}/dashboard_et.html", "w", encoding="utf-8") as f:
    f.write(out)

print(f"wrote {OUT}/dashboard_et.html ({len(out):,} bytes) from {len(flat)} strings")

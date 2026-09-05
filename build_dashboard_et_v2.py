#!/usr/bin/env python3
"""
Assembles output/dashboard.html: the dashboard's canonical Estonian build using
the English dashboard's template/app.js
structure (charts, scorecard bar, interactive waste-lever chart, secondary
effects section) rendered with Estonian text instead of English.

This is the canonical dashboard build. The former English dashboard and older
Estonian layout are no longer emitted into output/.

It reuses the same template.html / app.js "engine" as the English build --
only the strings file and the static methodology-body HTML differ -- so any
future edit to template.html or app.js's structure (not just its text)
automatically applies here too.

Reads:
  src/dashboard/template.html            -- same page skeleton as the English build
  src/dashboard/app.js                   -- same rendering logic as the English build
  output/strings_et_v2.json              -- user-edited Estonian strings
  src/dashboard/strings_et_v2.json       -- fallback for newly added strings
  src/dashboard/methodology_body_et.html -- static methodology section content, Estonian
  output/dashboard_data_et.json          -- the Estonian-translated data export (same schema
                                             and numbers as dashboard_data.json, but with
                                             food-group/item names, notes, and flag reasons
                                             already translated -- built earlier alongside
                                             the existing Estonian dashboard)

Writes:
  output/dashboard.html

Usage: python3 build_dashboard_et_v2.py   (run from the project root)
"""
import json
import pathlib
import re
from src.dashboard.localize_content import localize_content

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src" / "dashboard"
OUT = ROOT / "output"

LOOKUP_KEYS = {"js.scen_label", "js.delta_label", "js.sex_map"}


def remove_ss_crosscheck_ranges(app_js: str) -> str:
    """Remove cross-check ranges from the canonical Estonian dashboard UI."""
    block_start = "      if(r.cross_check_low_pct !== null && r.cross_check_high_pct !== null){"
    block_end = "      var status = statusOf(pct);"
    start = app_js.index(block_start)
    end = app_js.index(block_end, start)
    app_js = app_js[:start] + app_js[end:]

    tooltip_line = (
        '          + (r.cross_check_low_pct !== null ? ttRow("@@js.tt.crosscheck_range@@", '
        "fmtPct(Math.min(r.cross_check_low_pct, r.cross_check_high_pct)) + '\\u2013' + "
        "fmtPct(Math.max(r.cross_check_low_pct, r.cross_check_high_pct))) : '')\n"
    )
    table_cell = (
        "    tr.appendChild(el('td','num tnum', r.cross_check_low_pct !== null ? "
        "(fmtPct(Math.min(r.cross_check_low_pct, r.cross_check_high_pct)) + '\\u2013' + "
        "fmtPct(Math.max(r.cross_check_low_pct, r.cross_check_high_pct))) : \"—\"));\n"
    )
    assert tooltip_line in app_js, "cross-check tooltip row not found"
    assert table_cell in app_js, "cross-check table cell not found"
    app_js = app_js.replace(tooltip_line, "", 1)
    app_js = app_js.replace(table_cell, "", 1)
    app_js = app_js.replace(
        "var SS_TABLE_NUM_COLS = [false,false,true,true,true,true,true,true,true,false];",
        "var SS_TABLE_NUM_COLS = [false,false,true,true,true,true,true,true,false];",
        1,
    )
    return app_js


def overlay_strings(base, edits):
    """Overlay user-edited strings without dropping newly added fallback keys."""
    merged = dict(base)
    for key, value in edits.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = overlay_strings(merged[key], value)
        else:
            merged[key] = value
    return merged


def flatten2(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict) and key not in LOOKUP_KEYS:
            out.update(flatten2(v, key))
        else:
            out[key] = v
    return out


def main():
    template = (SRC / "template.html").read_text(encoding="utf-8")
    app_js = remove_ss_crosscheck_ranges(
        (SRC / "app.js").read_text(encoding="utf-8")
    )
    meth_body = (SRC / "methodology_body_et.html").read_text(encoding="utf-8")
    data_json = (OUT / "dashboard_data_et.json").read_text(encoding="utf-8")

    with open(SRC / "strings_et_v2.json", encoding="utf-8") as f:
        fallback_strings = json.load(f)
    with open(OUT / "strings_et_v2.json", encoding="utf-8") as f:
        user_strings = json.load(f)
    strings_nested = overlay_strings(fallback_strings, user_strings)
    data, meth_body = localize_content(strings_nested, json.loads(data_json), meth_body)
    data_json = json.dumps(data, ensure_ascii=False)
    flat = flatten2(strings_nested)

    json.loads(data_json)

    for key, val in flat.items():
        token = "{{" + key + "}}"
        if token in template:
            if not isinstance(val, str):
                continue
            template = template.replace(token, val)
    # This distribution contains only Estonian pages, so omit the English switch.
    template = re.sub(
        r'\s*<a href="[^"]*" class="lang-switch" id="lang-switch">[^<]*</a>',
        "",
        template,
    )
    leftover = re.findall(r"\{\{[a-z0-9_.]+\}\}", template)
    if leftover:
        print("WARNING: unresolved template placeholders:", leftover)

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

    assert "__DASHBOARD_DATA__" in template, "template missing data placeholder"
    assert "__APP_JS__" in template, "template missing app.js placeholder"
    assert '<div id="meth-body"></div>' in template, \
        "template missing methodology-body placeholder"

    html = template.replace("__DASHBOARD_DATA__", data_json).replace("__APP_JS__", app_js)
    html = html.replace(
        '<div id="meth-body"></div>',
        '<div id="meth-body">' + meth_body + "</div>",
    )

    out_path = OUT / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path} ({len(html):,} bytes) from {len(flat)} strings")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Assembles the self-contained dashboard HTML from its source pieces.

Reads:
  src/dashboard/template.html         -- page skeleton, CSS, placeholders
  src/dashboard/app.js                -- rendering logic
  src/dashboard/methodology_body.html -- static methodology section content
  output/dashboard_data.json          -- data export (produced by
                                          src/export_dashboard_data.py)

Writes:
  output/dashboard.html               -- the final, single-file dashboard

Run this any time the underlying data, model, or dashboard source files
change. It performs no computation of its own -- it is pure templating,
so the model (Python) and the presentation (HTML/JS + static JSON) stay
decoupled, per plans/PLAN.md Section 6.

Usage: python3 build_dashboard.py   (run from the project root)
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src" / "dashboard"
OUT = ROOT / "output"


def main():
    template = (SRC / "template.html").read_text(encoding="utf-8")
    app_js = (SRC / "app.js").read_text(encoding="utf-8")
    meth_body = (SRC / "methodology_body.html").read_text(encoding="utf-8")
    data_json = (OUT / "dashboard_data.json").read_text(encoding="utf-8")

    # sanity check: the data export must be valid JSON before it gets
    # embedded verbatim into the page
    json.loads(data_json)

    assert "__DASHBOARD_DATA__" in template, "template missing data placeholder"
    assert "__APP_JS__" in template, "template missing app.js placeholder"
    assert '<div class="appendix-body" id="meth-body"></div>' in template, \
        "template missing methodology-body placeholder"

    html = template.replace("__DASHBOARD_DATA__", data_json).replace("__APP_JS__", app_js)
    html = html.replace(
        '<div class="appendix-body" id="meth-body"></div>',
        '<div class="appendix-body" id="meth-body">' + meth_body + "</div>",
    )

    out_path = OUT / "dashboard.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"wrote {out_path} ({len(html):,} bytes)")


if __name__ == "__main__":
    main()

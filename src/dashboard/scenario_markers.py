"""Make baseline correction markers follow the selected demand scenario.

Production and the baseline loss/feed fractions remain fixed. Missing corrections
stay missing; this does not introduce new estimates or combine feed and waste.
"""


def apply_scenario_markers(app_js: str) -> str:
    helper = '''function scenarioAdjustedPct(row, field, scenarioPct){
  var baseline = row.scenario_A_pct;
  var adjusted = row[field];
  if(!Number.isFinite(baseline) || baseline <= 0 ||
     !Number.isFinite(adjusted) || !Number.isFinite(scenarioPct)) return null;
  return adjusted * scenarioPct / baseline;
}
'''
    app_js = app_js.replace('function renderSSChart(){', helper + 'function renderSSChart(){', 1)
    start = app_js.index('function renderSSChart(){')
    end = app_js.index("document.getElementById('scenario-hint')", start)
    chart = app_js[start:end]
    chart = chart.replace('    var pct = r[pctKey];', '''    var pct = r[pctKey];
    var wastePct = scenarioAdjustedPct(r, 'waste_adjusted_pct', pct);
    var feedPct = scenarioAdjustedPct(r, 'feed_adjusted_low_bound_pct', pct);''', 1)
    chart = chart.replace('r.waste_adjusted_pct', 'wastePct')
    chart = chart.replace('r.feed_adjusted_low_bound_pct', 'feedPct')
    app_js = app_js[:start] + chart + app_js[end:]
    start = app_js.index('function renderSSTable(')
    end = app_js.index('  table.appendChild(tbody);', start)
    table = app_js[start:end]
    table = table.replace("    var tr = el('tr');", """    var tr = el('tr');
    var wastePct = scenarioAdjustedPct(r, 'waste_adjusted_pct', r[pctKey]);
    var feedPct = scenarioAdjustedPct(r, 'feed_adjusted_low_bound_pct', r[pctKey]);""", 1)
    table = table.replace('r.waste_adjusted_pct', 'wastePct')
    table = table.replace('r.feed_adjusted_low_bound_pct', 'feedPct')
    # Correction columns follow the active scenario; the four main columns stay fixed.
    table = table.replace("htr.appendChild(el('th',", "if(i === 6 || i === 7) h += ' — ' + SCEN_LABEL[currentScenario];\n    htr.appendChild(el('th',", 1)
    return app_js[:start] + table + app_js[end:]

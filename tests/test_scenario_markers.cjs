const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('output/dashboard.html', 'utf8');
const helper = source.match(/function scenarioAdjustedPct\([\s\S]*?\n\}/);
assert.ok(helper, 'Scenario-aware marker conversion must exist');
const rendering = source.slice(source.indexOf('function renderSSChart(){'), source.indexOf('/*', source.indexOf('function renderSSTable(')));
assert.ok(!rendering.includes('r.waste_adjusted_pct'), 'Chart, tooltip and table must not display baseline waste directly');
assert.ok(!rendering.includes('r.feed_adjusted_low_bound_pct'), 'Chart, tooltip and table must not display baseline feed directly');
assert.ok(rendering.includes("h += ' — ' + SCEN_LABEL[currentScenario]"), 'Correction table headers must identify their scenario');
const ctx = {};
vm.createContext(ctx);
vm.runInContext(helper[0], ctx);
const data = JSON.parse(fs.readFileSync('output/dashboard_data_et.json', 'utf8'));
let checks = 0;
for (const row of data.food_groups) {
  for (const scenario of ['A', 'B', 'C', 'C2']) {
    const pct = row[`scenario_${scenario}_pct`];
    for (const field of ['waste_adjusted_pct', 'feed_adjusted_low_bound_pct']) {
      const actual = ctx.scenarioAdjustedPct(row, field, pct);
      if (row[field] == null || pct == null || !(row.scenario_A_pct > 0)) {
        assert.equal(actual, null);
      } else {
        assert.ok(Math.abs(actual - row[field] * pct / row.scenario_A_pct) < 1e-9);
        assert.ok(actual <= pct + 0.1, 'Loss/feed adjustment cannot improve self-sufficiency');
      }
      checks++;
    }
  }
}
const bread = data.food_groups.find(r => r.subitem === 'Kiudainerikas leib/pagaritooted');
assert.ok(Math.abs(ctx.scenarioAdjustedPct(bread, 'waste_adjusted_pct', bread.scenario_B_pct) - 132.1) < 0.1);
assert.equal(ctx.scenarioAdjustedPct({scenario_A_pct: 0, waste_adjusted_pct: 0}, 'waste_adjusted_pct', 0), null);
console.log(`${checks} marker cases passed, including bread TAI and missing/zero baselines`);

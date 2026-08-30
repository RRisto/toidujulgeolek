(function(){
"use strict";
var DATA = JSON.parse(document.getElementById('dashboard-data').textContent);

/* ---------------------------------------------------------------------
   helpers
   --------------------------------------------------------------------- */
function el(tag, cls, text){
  var e = document.createElement(tag);
  if(cls) e.className = cls;
  if(text !== undefined && text !== null) e.textContent = text;
  return e;
}
function fmtPct(v, digits){
  if(v === null || v === undefined) return "—";
  digits = digits === undefined ? 1 : digits;
  return v.toFixed(digits) + "%";
}
function fmtG(v){
  if(v === null || v === undefined) return "—";
  return v.toFixed(1) + " g";
}
function fmtT(v){
  if(v === null || v === undefined) return "—";
  return Math.round(v).toLocaleString("en-US") + " t";
}
function statusOf(pct){
  if(pct === null || pct === undefined) return "neutral";
  if(pct < 50) return "critical";
  if(pct < 100) return "warning";
  return "good";
}
function statusVar(status){
  return status === "good" ? "var(--dv-good)"
       : status === "warning" ? "var(--dv-warning)"
       : status === "critical" ? "var(--dv-critical)"
       : "var(--muted)";
}
function statusLabel(status){
  return status === "good" ? "Self-sufficient"
       : status === "warning" ? "Import-dependent"
       : status === "critical" ? "Critical dependency"
       : "No resolved figure";
}

var tooltipEl = document.getElementById('tooltip');
function showTooltip(evt, html){
  tooltipEl.innerHTML = "";
  var frag = document.createRange().createContextualFragment(html);
  tooltipEl.appendChild(frag);
  tooltipEl.classList.add('show');
  positionTooltip(evt);
}
function positionTooltip(evt){
  var x = evt.clientX, y = evt.clientY;
  var pad = 14;
  var rect = tooltipEl.getBoundingClientRect();
  var left = x + pad;
  var top = y + pad;
  if(left + rect.width > window.innerWidth - 8) left = x - rect.width - pad;
  if(top + rect.height > window.innerHeight - 8) top = y - rect.height - pad;
  tooltipEl.style.left = left + "px";
  tooltipEl.style.top = top + "px";
}
function hideTooltip(){ tooltipEl.classList.remove('show'); }
function ttRow(label, val){
  return '<div class="tt-row"><span>' + escapeHtml(label) + '</span><span class="tt-val">' + escapeHtml(val) + '</span></div>';
}
function escapeHtml(s){
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

/* generic table-view toggle wiring */
function wireTableToggle(btnSelector, tableId){
  var btn = document.querySelector('[data-table-toggle="' + tableId + '"]');
  var box = document.getElementById(tableId);
  if(!btn) return;
  btn.addEventListener('click', function(){
    var hidden = box.hasAttribute('hidden');
    if(hidden){ box.removeAttribute('hidden'); btn.textContent = "Hide table"; }
    else{ box.setAttribute('hidden',''); btn.textContent = "View as table"; }
  });
}

/* ---------------------------------------------------------------------
   01 — scorecard
   --------------------------------------------------------------------- */
(function renderScorecard(){
  var h = DATA.headline;
  var wrap = document.getElementById('scorecard-tiles');
  var tiles = [
    {
      label: "Scenario A — status quo",
      value: fmtPct(h.scenario_A_weighted_pct, 0),
      note: "Tonnage-weighted, covers " + h.scenario_A_coverage_pct_of_tonnage + "% of national demand by mass. High because dairy and grain — both strongly self-sufficient — dominate the weighting; weak categories like vegetables and fruit don't disappear, they're just outweighed here. See section 02.",
      accent: true
    },
    {
      label: "Scenario B — TAI-recommended diet",
      value: fmtPct(h.scenario_B_weighted_pct, 0),
      note: "Same production, same weighting basis — demand shifted to what TAI recommends. The drop reflects recommended intake rising fastest in categories Estonia already struggles to supply. See section 05.",
      accent: false
    },
    {
      label: "Scenario C — EAT-Lancet diet",
      value: fmtPct(h.scenario_C_weighted_pct, 0),
      note: "Same production, same weighting basis — demand shifted to the EAT-Lancet Planetary Health Diet, an international reference diet, population-scaled to Estonia's energy needs. Higher than Scenario A mainly because EAT-Lancet recommends markedly less dairy and meat than Estonia actually eats. See section 02.",
      accent: false
    },
    {
      label: "With 25% less household waste",
      value: fmtPct(h.scenario_A_waste25_weighted_pct, 0),
      note: "Scenario A, if households cut food waste by a quarter — a demand-side efficiency lever, not a change to production.",
      accent: false
    },
    {
      label: "With 50% less household waste",
      value: fmtPct(h.scenario_A_waste50_weighted_pct, 0),
      note: "Scenario A, if households halved food waste. Effect sizes are modest — waste reduction eases the picture, it doesn't resolve the structural gaps.",
      accent: false
    }
  ];
  tiles.forEach(function(t){
    var tile = el('div','tile' + (t.accent ? ' accent' : ''));
    tile.appendChild(el('span','tile-label', t.label));
    tile.appendChild(el('div','tile-value tnum', t.value));
    tile.appendChild(el('div','tile-note', t.note));
    wrap.appendChild(tile);
  });
})();

/* ---------------------------------------------------------------------
   02 — self-sufficiency by food group (scenario-toggleable hbar chart)
   --------------------------------------------------------------------- */
var currentScenario = "A";
var SCEN_KEYS = {
  A: { pct: "scenario_A_pct", disp: "scenario_A_pct_display" },
  B: { pct: "scenario_B_pct", disp: "scenario_B_pct_display" },
  C: { pct: "scenario_C_pct", disp: "scenario_C_pct_display" }
};
function renderSSChart(){
  var container = document.getElementById('ss-chart');
  container.innerHTML = "";
  var pctKey = SCEN_KEYS[currentScenario].pct;
  var dispKey = SCEN_KEYS[currentScenario].disp;

  var rows = DATA.food_groups.slice();
  rows.sort(function(a,b){
    var av = a[pctKey], bv = b[pctKey];
    if(av === null && bv === null) return 0;
    if(av === null) return 1;
    if(bv === null) return -1;
    return bv - av;
  });

  var numericVals = rows.map(function(r){ return r[pctKey]; }).filter(function(v){ return v !== null; });
  var maxPct = Math.max.apply(null, numericVals.concat([100]));
  maxPct = maxPct * 1.08;

  rows.forEach(function(r){
    var row = el('div','hbar-row');
    var label = el('div','hbar-label');
    label.appendChild(el('span','grp', r.pyramid_group));
    label.appendChild(document.createTextNode(r.subitem));
    row.appendChild(label);

    var track = el('div','hbar-track');
    var pct = r[pctKey];

    if(pct === null){
      var badge = el('span','pill neutral pill-wrap');
      var dot = el('span','dot'); dot.style.background = "var(--muted)";
      badge.appendChild(dot);
      badge.appendChild(document.createTextNode(r.data_status.indexOf('gap') === 0 || r.data_status.indexOf('assumed') > -1 ? "no single figure — " + r[dispKey] : r[dispKey]));
      badge.style.marginTop = "3px";
      track.style.display = "flex"; track.style.alignItems = "center";
      track.appendChild(badge);
    } else {
      var baselinePos = (100/maxPct*100);
      var baseline = el('div','hbar-baseline');
      baseline.style.left = baselinePos + "%";
      track.appendChild(baseline);

      var status = statusOf(pct);
      var fill = el('div','hbar-fill');
      var widthPct = Math.max(pct/maxPct*100, 0.6);
      fill.style.width = widthPct + "%";
      fill.style.background = statusVar(status);
      fill.tabIndex = 0;
      fill.setAttribute('role','img');
      fill.setAttribute('aria-label', r.pyramid_group + ' ' + r.subitem + ': ' + fmtPct(pct));

      var tip = el('span','hbar-tip tnum', fmtPct(pct));
      if(widthPct > 14){
        tip.style.right = "8px"; tip.style.color = "#fff"; tip.style.mixBlendMode="normal";
        fill.appendChild(tip);
      } else {
        tip.style.left = "calc(100% + 8px)"; tip.style.color = "var(--ink)";
        fill.appendChild(tip);
      }
      track.appendChild(fill);

      var showTt = function(evt){
        var html = '<div class="tt-title">' + escapeHtml(r.pyramid_group) + ' — ' + escapeHtml(r.subitem) + '</div>'
          + ttRow('Scenario ' + currentScenario, fmtPct(pct))
          + (r.feed_adjusted_low_bound_pct !== null ? ttRow('Feed-adjusted lower bound', fmtPct(r.feed_adjusted_low_bound_pct)) : '')
          + ttRow('Status', statusLabel(status))
          + ttRow('Data status', r.data_status);
        showTooltip(evt, html);
      };
      fill.addEventListener('mousemove', showTt);
      fill.addEventListener('mouseenter', showTt);
      fill.addEventListener('mouseleave', hideTooltip);
      fill.addEventListener('focus', function(evt){
        var r0 = fill.getBoundingClientRect();
        showTt({clientX: r0.right, clientY: r0.top});
      });
      fill.addEventListener('blur', hideTooltip);

      if(r.feed_adjusted_low_bound_pct !== null){
        var marker = el('div','hbar-marker');
        marker.style.left = Math.min(r.feed_adjusted_low_bound_pct/maxPct*100, 100) + "%";
        marker.style.background = "var(--grain)";
        marker.title = "Feed-adjusted lower bound: " + fmtPct(r.feed_adjusted_low_bound_pct);
        track.appendChild(marker);
      }
    }
    row.appendChild(track);
    container.appendChild(row);
  });

  renderSSTable(rows, pctKey, dispKey);
  document.getElementById('scenario-hint').textContent = currentScenario === "A"
    ? "Today's actual diet against today's production."
    : currentScenario === "B"
    ? "If everyone ate exactly as TAI recommends — production unchanged."
    : "If everyone ate the EAT-Lancet Planetary Health Diet, population-scaled to Estonia's energy needs — production unchanged.";
}

function renderSSTable(rows, pctKey, dispKey){
  var box = document.getElementById('ss-table');
  box.innerHTML = "";
  var table = el('table','data-table');
  var thead = el('thead');
  var htr = el('tr');
  ["Food group","Item","Scenario A","Scenario B","Scenario C","Feed-adjusted bound","Data status"].forEach(function(h){
    htr.appendChild(el('th', h.indexOf("Scenario")===0 || h==="Feed-adjusted bound" ? 'num' : '', h));
  });
  thead.appendChild(htr); table.appendChild(thead);
  var tbody = el('tbody');
  rows.forEach(function(r){
    var tr = el('tr');
    tr.appendChild(el('td','strong', r.pyramid_group));
    tr.appendChild(el('td','', r.subitem));
    tr.appendChild(el('td','num tnum', r.scenario_A_pct_display));
    tr.appendChild(el('td','num tnum', r.scenario_B_pct_display));
    tr.appendChild(el('td','num tnum', r.scenario_C_pct_display));
    tr.appendChild(el('td','num tnum', r.feed_adjusted_low_bound_pct !== null ? fmtPct(r.feed_adjusted_low_bound_pct) : "—"));
    tr.appendChild(el('td','', r.data_status));
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  box.appendChild(table);
}

document.querySelectorAll('#scenario-toggle button').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.querySelectorAll('#scenario-toggle button').forEach(function(b){ b.setAttribute('aria-pressed','false'); });
    btn.setAttribute('aria-pressed','true');
    currentScenario = btn.getAttribute('data-scenario');
    renderSSChart();
  });
});
renderSSChart();
wireTableToggle(null,'ss-table');

/* ---------------------------------------------------------------------
   03 — critical dependency callouts
   --------------------------------------------------------------------- */
(function renderCallouts(){
  var grid = document.getElementById('callout-grid');
  var items = DATA.food_groups.filter(function(r){
    return r.flags.below_50_scenario_A === 'Y' || r.flags.feed_adjusted_extends_concern === 'Y' || r.flags.unresolved_data_gap === 'Y';
  });
  items.forEach(function(r){
    var severity = (r.flags.below_50_scenario_A === 'Y' || r.flags.feed_adjusted_extends_concern === 'Y') ? 'critical' : 'warning';
    var card = el('div','callout' + (severity === 'warning' ? ' warning-border' : ''));
    var head = el('div','callout-head');
    head.appendChild(el('h3','', r.pyramid_group + ' — ' + r.subitem));
    var pill = el('span','pill ' + severity);
    var dot = el('span','dot'); dot.style.background = severity === 'critical' ? 'var(--dv-critical)' : 'var(--dv-warning)';
    pill.appendChild(dot);
    pill.appendChild(document.createTextNode(severity === 'critical' ? 'Critical' : 'Data gap'));
    head.appendChild(pill);
    card.appendChild(head);
    var body = el('div','callout-body');
    body.textContent = r.flag_reason || r.note;
    card.appendChild(body);
    grid.appendChild(card);
  });
})();

/* ---------------------------------------------------------------------
   04 — consumption comparison (dumbbell, national + demographic filter)
   --------------------------------------------------------------------- */
var segSelect = document.getElementById('segment-select');
(function initSegments(){
  var optNat = el('option','', 'National (all ages)');
  optNat.value = "__national__";
  segSelect.appendChild(optNat);
  DATA.segments_available.forEach(function(s){
    var opt = el('option','', s.replace(/\b\w/g, function(c){return c.toUpperCase();}));
    opt.value = s;
    segSelect.appendChild(opt);
  });
})();

function renderConsChart(){
  var container = document.getElementById('cons-chart');
  container.innerHTML = "";
  var sel = segSelect.value;
  var rows;
  if(sel === "__national__"){
    rows = DATA.consumption_national.map(function(r){
      return {
        pyramid_group: r.pyramid_group, subitem: r.subitem,
        recommended: r.recommended_g_per_day, actual: r.actual_g_per_day,
        assessment: r.assessment
      };
    });
    document.getElementById('segment-hint').textContent = "Whole population, weighted by age and sex.";
  } else {
    var parts = sel.split(" ");
    var sex = parts.pop();
    var ageBand = parts.join(" ");
    rows = DATA.consumption_by_segment.filter(function(r){ return r.age_band === ageBand && r.sex === sex; })
      .map(function(r){
        return { pyramid_group: r.pyramid_group, subitem: r.subitem, recommended: r.recommended_g_per_day, actual: r.actual_g_per_day, assessment: null };
      });
    document.getElementById('segment-hint').textContent = "Ages " + ageBand + ", " + sex + ".";
  }
  rows.sort(function(a,b){ return (b.recommended||0) - (a.recommended||0); });

  var maxVal = Math.max.apply(null, rows.map(function(r){ return Math.max(r.recommended||0, r.actual||0); }).concat([1])) * 1.12;

  rows.forEach(function(r){
    var row = el('div','hbar-row');
    var label = el('div','hbar-label');
    label.appendChild(el('span','grp', r.pyramid_group));
    label.appendChild(document.createTextNode(r.subitem));
    row.appendChild(label);

    var track = el('div','hbar-track');
    if(r.actual === null){
      track.style.display="flex"; track.style.alignItems="center";
      var badge = el('span','pill neutral pill-wrap');
      badge.appendChild(document.createTextNode('not measured — no RTU011 data'));
      track.appendChild(badge);
    } else {
      var recPos = Math.min(r.recommended/maxVal*100, 100);
      var actPos = Math.min(r.actual/maxVal*100, 100);
      var lo = Math.min(recPos, actPos), hi = Math.max(recPos, actPos);
      var connector = el('div');
      connector.style.position = "absolute"; connector.style.top = "50%"; connector.style.height="2px";
      connector.style.left = lo + "%"; connector.style.width = (hi-lo) + "%";
      connector.style.background = "var(--line)"; connector.style.transform = "translateY(-50%)";
      track.appendChild(connector);

      function marker(pos, color, label2, value){
        var m = el('div');
        m.style.position="absolute"; m.style.top="50%"; m.style.left = pos + "%";
        m.style.width="12px"; m.style.height="12px"; m.style.borderRadius="50%";
        m.style.background = color; m.style.transform="translate(-50%,-50%)";
        m.style.border = "2px solid var(--surface)"; m.style.cursor="pointer";
        m.tabIndex = 0;
        var fn = function(evt){
          var html = '<div class="tt-title">' + escapeHtml(r.pyramid_group) + ' — ' + escapeHtml(r.subitem) + '</div>'
            + ttRow(label2, value.toFixed(1) + ' g/day');
          showTooltip(evt, html);
        };
        m.addEventListener('mousemove', fn);
        m.addEventListener('mouseenter', fn);
        m.addEventListener('mouseleave', hideTooltip);
        return m;
      }
      track.appendChild(marker(recPos, "var(--grain)", "TAI recommended", r.recommended));
      track.appendChild(marker(actPos, "var(--dv-blue)", "Actual consumption", r.actual));
    }
    row.appendChild(track);
    container.appendChild(row);
  });

  renderConsTable(rows);
}
function renderConsTable(rows){
  var box = document.getElementById('cons-table');
  box.innerHTML = "";
  var table = el('table','data-table');
  var thead = el('thead'); var htr = el('tr');
  ["Food group","Item","Recommended (g/day)","Actual (g/day)","Ratio"].forEach(function(h){
    htr.appendChild(el('th', h.indexOf('g/day')>-1 || h==="Ratio" ? 'num' : '', h));
  });
  thead.appendChild(htr); table.appendChild(thead);
  var tbody = el('tbody');
  rows.forEach(function(r){
    var tr = el('tr');
    tr.appendChild(el('td','strong', r.pyramid_group));
    tr.appendChild(el('td','', r.subitem));
    tr.appendChild(el('td','num tnum', r.recommended !== null ? r.recommended.toFixed(1) : "—"));
    tr.appendChild(el('td','num tnum', r.actual !== null ? r.actual.toFixed(1) : "not measured"));
    tr.appendChild(el('td','num tnum', (r.actual !== null && r.recommended) ? (r.actual/r.recommended).toFixed(2) + "x" : "—"));
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  box.appendChild(table);
}
segSelect.addEventListener('change', renderConsChart);
renderConsChart();
wireTableToggle(null,'cons-table');

/* ---------------------------------------------------------------------
   05 — scenario delta (diverging bar)
   --------------------------------------------------------------------- */
var currentDelta = "B";
var DELTA_LABEL = { B: "Scenario B", C: "Scenario C" };
function renderDeltaChart(){
  var container = document.getElementById('delta-chart');
  container.innerHTML = "";
  var pctKey = currentDelta === "B" ? "scenario_B_pct" : "scenario_C_pct";
  var labelName = DELTA_LABEL[currentDelta];
  var rows = DATA.food_groups.filter(function(r){ return r.scenario_A_pct !== null && r[pctKey] !== null; })
    .map(function(r){ return { pyramid_group:r.pyramid_group, subitem:r.subitem, delta: r[pctKey] - r.scenario_A_pct, a:r.scenario_A_pct, b:r[pctKey] }; });
  rows.sort(function(a,b){ return a.delta - b.delta; });
  var maxAbs = Math.max.apply(null, rows.map(function(r){ return Math.abs(r.delta); })) * 1.1;

  rows.forEach(function(r){
    var row = el('div','hbar-row');
    var label = el('div','hbar-label');
    label.appendChild(el('span','grp', r.pyramid_group));
    label.appendChild(document.createTextNode(r.subitem));
    row.appendChild(label);

    var track = el('div','hbar-track');
    var mid = el('div','hbar-baseline'); mid.style.left = "50%"; track.appendChild(mid);

    var pctOfHalf = Math.abs(r.delta)/maxAbs*50;
    var barW = Math.max(pctOfHalf,0.6);
    var fill = el('div','hbar-fill');
    fill.style.width = barW + "%";
    fill.style.background = r.delta < 0 ? "var(--dv-critical)" : "var(--dv-good)";
    if(r.delta < 0){ fill.style.left = (50 - pctOfHalf) + "%"; }
    else { fill.style.left = "50%"; }
    fill.tabIndex = 0;
    var tipTxt = (r.delta>=0?"+":"") + r.delta.toFixed(1) + " pt";
    var tip = el('span','hbar-tip tnum', tipTxt);
    /* Position the tip relative to the fill element itself (not the track) so long
       bars near the track's outer edge can never push the label into the row-label
       column. Wide bars get the label inside, in white; narrow bars keep it outside. */
    if(barW > 14){
      tip.style.color = "#fff";
      if(r.delta < 0){ tip.style.left = "8px"; }
      else { tip.style.right = "8px"; }
    } else {
      tip.style.color = "var(--ink)";
      if(r.delta < 0){ tip.style.right = "calc(100% + 8px)"; }
      else { tip.style.left = "calc(100% + 8px)"; }
    }
    fill.appendChild(tip);
    track.appendChild(fill);

    var fn = function(evt){
      var html = '<div class="tt-title">' + escapeHtml(r.pyramid_group) + ' — ' + escapeHtml(r.subitem) + '</div>'
        + ttRow('Scenario A', fmtPct(r.a)) + ttRow(labelName, fmtPct(r.b)) + ttRow('Change', tipTxt);
      showTooltip(evt, html);
    };
    fill.addEventListener('mousemove', fn);
    fill.addEventListener('mouseenter', fn);
    fill.addEventListener('mouseleave', hideTooltip);

    row.appendChild(track);
    container.appendChild(row);
  });

  document.getElementById('delta-hint').textContent = currentDelta === "B"
    ? "TAI recommends eating more of several categories Estonia is already worst at supplying domestically."
    : "EAT-Lancet reduces demand for most animal products (raising self-sufficiency) but sharply raises demand for oils/fats — rapeseed drops from 69.3% to 27.0%, a new critical dependency that doesn't exist under Scenario A or B.";
}

document.querySelectorAll('#delta-toggle button').forEach(function(btn){
  btn.addEventListener('click', function(){
    document.querySelectorAll('#delta-toggle button').forEach(function(b){ b.setAttribute('aria-pressed','false'); });
    btn.setAttribute('aria-pressed','true');
    currentDelta = btn.getAttribute('data-delta');
    renderDeltaChart();
  });
});
renderDeltaChart();

/* ---------------------------------------------------------------------
   06 — waste module
   --------------------------------------------------------------------- */
(function renderWasteChart(){
  var container = document.getElementById('waste-chart');
  var rows = DATA.waste.slice().sort(function(a,b){ return (b.waste_tonnes_year||0) - (a.waste_tonnes_year||0); });
  var maxT = Math.max.apply(null, rows.map(function(r){ return r.waste_tonnes_year||0; })) * 1.05;

  rows.forEach(function(r){
    var row = el('div','hbar-row');
    var label = el('div','hbar-label');
    label.appendChild(el('span','grp', r.pyramid_group === '(all groups)' ? 'Unattributed' : r.pyramid_group));
    label.appendChild(document.createTextNode(r.subitem.length > 34 ? r.subitem.slice(0,32)+'…' : r.subitem));
    row.appendChild(label);

    var trackWrap = el('div'); trackWrap.style.flex = "1 1 auto";
    var stack = el('div','stack-track');
    var totalWidthPct = Math.max((r.waste_tonnes_year||0)/maxT*100, 1);
    stack.style.width = totalWidthPct + "%";

    if(r.household_waste_tonnes_year !== null && r.household_share_of_groups_waste_pct !== null){
      var hhShare = r.household_share_of_groups_waste_pct;
      var segHH = el('div','stack-seg'); segHH.style.width = hhShare + "%"; segHH.style.background="var(--dv-orange)";
      var segOther = el('div','stack-seg'); segOther.style.width = (100-hhShare) + "%"; segOther.style.background="var(--dv-blue)";
      var mkFn = function(name, val){
        return function(evt){
          var html = '<div class="tt-title">' + escapeHtml(r.pyramid_group) + ' — ' + escapeHtml(r.subitem) + '</div>'
            + ttRow('Total waste', fmtT(r.waste_tonnes_year))
            + ttRow(name, val)
            + ttRow('Loss rate vs. consumption', r.loss_rate_vs_consumption_pct !== null ? r.loss_rate_vs_consumption_pct + '%' : '—');
          showTooltip(evt, html);
        };
      };
      segHH.addEventListener('mousemove', mkFn('Household share', hhShare.toFixed(0) + '% (' + fmtT(r.household_waste_tonnes_year) + ')'));
      segHH.addEventListener('mouseleave', hideTooltip);
      segOther.addEventListener('mousemove', mkFn('Other stages', (100-hhShare).toFixed(0) + '%'));
      segOther.addEventListener('mouseleave', hideTooltip);
      stack.appendChild(segHH); stack.appendChild(segOther);
    } else {
      var seg = el('div','stack-seg'); seg.style.width="100%"; seg.style.background="var(--muted)"; seg.style.opacity="0.55";
      seg.addEventListener('mousemove', function(evt){
        showTooltip(evt, '<div class="tt-title">Unattributed</div>' + ttRow('Total', fmtT(r.waste_tonnes_year)) + ttRow('Note','Cross-category residue, not allocated to one food group'));
      });
      seg.addEventListener('mouseleave', hideTooltip);
      stack.appendChild(seg);
    }
    trackWrap.appendChild(stack);
    row.appendChild(trackWrap);

    var pctLabel = el('div', '', r.pct_of_total_sei_waste !== null ? r.pct_of_total_sei_waste.toFixed(0)+'%' : '');
    pctLabel.style.width="42px"; pctLabel.style.flex="0 0 42px"; pctLabel.style.fontSize="12px";
    pctLabel.style.color="var(--muted)"; pctLabel.classList.add('tnum');
    row.appendChild(pctLabel);

    container.appendChild(row);
  });
})();

(function renderWasteLever(){
  var wrap = document.getElementById('waste-lever-list');
  var rows = DATA.waste.filter(function(r){ return r.required_production_inflator !== null; })
    .sort(function(a,b){ return b.required_production_inflator - a.required_production_inflator; });
  rows.forEach(function(r){
    var line = el('div');
    line.style.display="flex"; line.style.justifyContent="space-between"; line.style.alignItems="center";
    line.style.padding="9px 0"; line.style.borderBottom="1px solid var(--line)"; line.style.fontSize="13px";
    var name = el('div');
    var strong = el('div','', r.subitem === '(total)' ? r.pyramid_group : r.subitem);
    strong.style.color="var(--ink)"; strong.style.fontWeight="500"; strong.style.fontSize="13px";
    name.appendChild(strong);
    line.appendChild(name);
    var vals = el('div','mono tnum');
    vals.style.color="var(--ink-soft)"; vals.style.fontSize="12.5px";
    vals.textContent = r.required_production_inflator.toFixed(2) + "x → " + r.inflator_25pct_cut.toFixed(2) + "x → " + r.inflator_50pct_cut.toFixed(2) + "x";
    line.appendChild(vals);
    wrap.appendChild(line);
  });
  var note = el('p'); note.style.color="var(--muted)"; note.style.fontSize="11.5px"; note.style.marginTop="12px";
  note.textContent = "Required-production multiplier: how much more must reach the supply chain than is actually eaten, today → at a 25% → at a 50% household-waste cut.";
  wrap.appendChild(note);
})();

/* ---------------------------------------------------------------------
   07 — methodology: FAOSTAT table + footer meta
   --------------------------------------------------------------------- */
(function renderFaostatTable(){
  var host = document.getElementById('faostat-table-host');
  if(!host) return;
  var table = el('table','data-table source-table');
  var thead = el('thead'); var htr = el('tr');
  ["Food group","FAOSTAT item (2022)","FAOSTAT self-sufficiency","This project's figure","Note"].forEach(function(h){
    htr.appendChild(el('th', h.indexOf('self-sufficiency')>-1 || h.indexOf("figure")>-1 ? 'num':'', h));
  });
  thead.appendChild(htr); table.appendChild(thead);
  var tbody = el('tbody');
  DATA.faostat_cross_check.forEach(function(r){
    var tr = el('tr');
    tr.appendChild(el('td','strong', r.pyramid_group));
    tr.appendChild(el('td','', r.faostat_item));
    tr.appendChild(el('td','num tnum', r.faostat_self_sufficiency_pct !== null ? r.faostat_self_sufficiency_pct + '%' : '—'));
    tr.appendChild(el('td','num tnum', r.project_self_sufficiency_pct !== null ? r.project_self_sufficiency_pct + '%' : '—'));
    tr.appendChild(el('td','', r.note));
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  host.appendChild(table);
})();

document.getElementById('footer-left').textContent = "Generated " + DATA.meta.generated + " · population " + DATA.meta.reference_years.population + " · production " + DATA.meta.reference_years.production_supply + " · consumption survey " + DATA.meta.reference_years.consumption_survey;

})();

const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

class FakeNode {
  constructor(tag, cls = '', text = '') {
    this.tag = tag;
    this.className = cls;
    this.textContent = text;
    this.children = [];
    this.style = {};
    this.attributes = {};
  }
  appendChild(child) { this.children.push(child); return child; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener() {}
}

const source = fs.readFileSync('output/dashboard.html', 'utf8');
const start = source.indexOf('(function renderScorecard(){');
const end = source.indexOf('/* ---------------------------------------------------------------------', start + 1);
assert.ok(start >= 0 && end > start, 'Rendered scorecard code must exist');

const container = new FakeNode('div', 'scorecard-chart');
const data = JSON.parse(fs.readFileSync('output/dashboard_data_et.json', 'utf8'));
const context = {
  DATA: data,
  document: {
    getElementById(id) {
      assert.equal(id, 'scorecard-chart');
      return container;
    },
    createTextNode(text) { return new FakeNode('#text', '', text); },
  },
  el(tag, cls, text) { return new FakeNode(tag, cls, text); },
  fmtPct(value, digits = 1) { return `${value.toFixed(digits)}%`; },
  statusOf() { return 'good'; },
  statusVar() { return 'green'; },
  escapeHtml(value) { return String(value); },
  ttRow() { return ''; },
  showTooltip() {},
  hideTooltip() {},
};
vm.createContext(context);
vm.runInContext(source.slice(start, end), context);

const labels = container.children.map(row => row.children[0].children[0].textContent);
assert.deepEqual(labels, [
  'Stsenaarium A — praegune olukord',
  'Stsenaarium B — TAI soovitatud toitumine',
  'Stsenaarium C — EAT-Lancet 2019 dieet',
  'Stsenaarium C.2 — EAT-Lancet 2025 dieet',
]);
console.log('Scorecard renders only the four diet scenarios');

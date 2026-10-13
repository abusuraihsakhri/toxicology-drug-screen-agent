"use strict";
const assert = require("node:assert/strict");
const { evaluateCase } = require("./app.js");
const input = (updates = {}) => ({
  task_id: "DEMO-1", target_identifier: "SPECIMEN-1", primary_metric: 25,
  secondary_metric: 12, status_descriptor: "NORMAL", is_critical_flag: false, ...updates
});
assert.equal(evaluateCase(input()).demo_status, "NO_RULES_TRIGGERED");
assert.equal(evaluateCase(input({ primary_metric: 25.01 })).total_alerts, 1);
assert.equal(evaluateCase(input({ secondary_metric: 12.01 })).total_alerts, 1);
assert.equal(evaluateCase(input({ status_descriptor: "discordant_anomaly" })).total_alerts, 1);
assert.equal(evaluateCase(input({ is_critical_flag: true })).overall_urgency, "CRITICAL_STAT_PANIC");
assert.equal(evaluateCase(input({ primary_metric: 30, secondary_metric: 13, status_descriptor: "FAIL", is_critical_flag: true })).total_alerts, 3);
for (const x of [NaN, Infinity, -Infinity, "", "abc"]) {
  assert.throws(() => evaluateCase(input({ primary_metric: x })), /finite|required/);
}
for (const id of ["test@example.com", "Jane Doe", "../secret", ""]) {
  assert.throws(() => evaluateCase(input({ task_id: id })), /Task and sample/);
}
assert.throws(() => evaluateCase(input({ status_descriptor: "<script>" })), /Status/);
console.log("Browser rule tests passed");

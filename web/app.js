"use strict";

// Browser-only demonstration of the three generic workers in agents/workers.py.
// These numeric thresholds are illustrative; they are NOT toxicology assay cutoffs.
function evaluateCase(raw) {
  if (!raw || typeof raw !== "object") throw new TypeError("A case object is required.");
  const task = String(raw.task_id ?? "").trim();
  const target = String(raw.target_identifier ?? "").trim();
  const descriptor = String(raw.status_descriptor ?? "").trim().toUpperCase();
  const safeId = /^[A-Za-z0-9_-]{1,64}$/;
  if (!safeId.test(task) || !safeId.test(target)) {
    throw new Error("Task and sample IDs must be 1–64 letters, digits, underscores or hyphens. Do not enter patient identifiers.");
  }
  if (!/^[A-Z0-9 _-]{1,80}$/.test(descriptor)) {
    throw new Error("Status is required and must be at most 80 letters, digits, spaces, underscores or hyphens.");
  }
  function metric(value, name) {
    if (value === null || value === undefined || String(value).trim() === "") {
      throw new Error(name + " is required.");
    }
    const number = Number(value);
    if (!Number.isFinite(number)) throw new Error(name + " must be a finite number.");
    return number;
  }
  const primary = metric(raw.primary_metric, "Primary measurement");
  const secondary = metric(raw.secondary_metric, "Secondary measurement");
  const critical = raw.is_critical_flag === true;
  const alerts = [];
  if (primary > 25) {
    alerts.push({
      origin_worker: "InvariantQCWorker",
      urgency: "ELEVATED_RISK",
      summary: "Demo primary threshold exceeded",
      technical_details: "Primary measurement " + primary + " > illustrative threshold 25."
    });
  }
  if (critical || secondary > 12) {
    alerts.push({
      origin_worker: "SafetyEscalationWorker",
      urgency: critical ? "CRITICAL_STAT_PANIC" : "ELEVATED_RISK",
      summary: "Demo secondary/critical rule triggered",
      technical_details: "Critical flag: " + critical + "; secondary measurement: " + secondary + "; illustrative threshold: 12."
    });
  }
  if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(x => descriptor.includes(x))) {
    alerts.push({
      origin_worker: "ProtocolConformanceWorker",
      urgency: "ELEVATED_RISK",
      summary: "Status keyword matched",
      technical_details: "Status descriptor contains a configured demo keyword."
    });
  }
  const criticalCount = alerts.filter(a => a.urgency === "CRITICAL_STAT_PANIC").length;
  const elevatedCount = alerts.filter(a => a.urgency === "ELEVATED_RISK").length;
  return {
    mode: "LOCAL_DEMONSTRATION",
    clinical_validation: "NONE",
    task_id: task,
    target_identifier: target,
    overall_urgency: criticalCount ? "CRITICAL_STAT_PANIC" : elevatedCount ? "ELEVATED_RISK" : "ROUTINE",
    demo_status: criticalCount ? "CRITICAL_FLAG_TRIGGERED" : elevatedCount ? "RULES_TRIGGERED" : "NO_RULES_TRIGGERED",
    total_alerts: alerts.length,
    alerts: alerts,
    disclaimer: "Illustrative software rules only. No drug identification, cross-reactivity assessment, LC-MS/MS planning or clinical decision is performed."
  };
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { evaluateCase };
}

if (typeof document !== "undefined") {
  const form = document.getElementById("audit-form");
  const output = document.getElementById("output");
  const download = document.getElementById("download");
  const count = document.getElementById("count");
  const verdict = document.getElementById("verdict");
  let lastResult = null;
  let processed = 0;
  form.addEventListener("submit", function (event) {
    event.preventDefault();
    try {
      const data = evaluateCase({
        task_id: document.getElementById("task").value,
        target_identifier: document.getElementById("target").value,
        primary_metric: document.getElementById("primary").value,
        secondary_metric: document.getElementById("secondary").value,
        status_descriptor: document.getElementById("status").value,
        is_critical_flag: document.getElementById("critical").checked
      });
      lastResult = data;
      processed += 1;
      output.textContent = JSON.stringify(data, null, 2);
      count.textContent = String(processed);
      verdict.textContent = data.demo_status.replaceAll("_", " ");
      download.disabled = false;
    } catch (error) {
      output.textContent = "Input error: " + error.message;
      verdict.textContent = "INVALID INPUT";
      download.disabled = true;
      lastResult = null;
    }
  });
  download.addEventListener("click", function () {
    if (!lastResult) return;
    const blob = new Blob([JSON.stringify(lastResult, null, 2) + "\n"], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "toxscreen-demo.json";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  });
}

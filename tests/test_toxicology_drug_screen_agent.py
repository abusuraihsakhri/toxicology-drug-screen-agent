"""
Automated Pytest Test Suite for Toxicology Drug Screen Agent.
Domain: Clinical & Biomedical AI
Standard: CAP / CLSI / ISO Standards
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel, SystemIntegrityStatus
from agents.workers import InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker
from agents.supervisor import SystemSupervisor
from cli import main


def test_phi_guard_enforcement():
    with pytest.raises(SecurityException):
        PHIGuard.assert_no_phi("Patient MRN-994827 blood culture positive for Staphylococcus")

    # Clean text passes
    PHIGuard.assert_no_phi("Analytical assay specimen KEY-001 optimal")


def test_phi_guard_redaction():
    redacted = PHIGuard.redact_phi("Contact patient at 555-123-4567 or test@example.com")
    assert "555-123-4567" not in redacted
    assert "test@example.com" not in redacted
    assert "[REDACTED_IDENTIFIER]" in redacted


def test_specialized_workers():
    # Worker 1: QC Invariant
    p1 = SystemTaskPayload(task_id="T1", target_identifier="KEY-01", primary_metric=35.0)
    alerts1 = InvariantQCWorker.evaluate(p1)
    assert len(alerts1) == 1
    assert alerts1[0].urgency == UrgencyLevel.ELEVATED

    # Worker 2: Safety
    p2 = SystemTaskPayload(task_id="T2", target_identifier="KEY-02", primary_metric=10.0, is_critical_flag=True)
    alerts2 = SafetyEscalationWorker.evaluate(p2)
    assert len(alerts2) == 1
    assert alerts2[0].urgency == UrgencyLevel.CRITICAL_STAT

    # Worker 3: Protocol Conformance
    p3 = SystemTaskPayload(task_id="T3", target_identifier="KEY-03", primary_metric=10.0, status_descriptor="DISCORDANT_ANOMALY")
    alerts3 = ProtocolConformanceWorker.evaluate(p3)
    assert len(alerts3) == 1


def test_supervisor_consensus_and_audit():
    supervisor = SystemSupervisor(model_provider="mock")
    payload = SystemTaskPayload(
        task_id="TASK-PROD-01",
        target_identifier="KEY-PROD-01",
        primary_metric=12.0,
        secondary_metric=4.0,
        status_descriptor="NOMINAL"
    )
    dossier = supervisor.process_task(payload)
    assert dossier.overall_urgency == UrgencyLevel.ROUTINE
    assert dossier.integrity_status == SystemIntegrityStatus.VALIDATED
    assert dossier.audit_hash != ""

    # Verify cryptographic audit trail
    assert AuditLogger.verify_integrity() is True

    # CLI tests
    assert main(["audit", "--task-id", "CLI-TEST-01"]) == 0
    assert main(["chat", "Explain", "specifications"]) == 0
    assert main(["verify-audit"]) == 0


def test_audit_trail_integrity():
    """Test that audit trail detects tampering."""
    trail = AuditTrail(secret_key="test-key-for-integrity-check")
    trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value1"})
    trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value2"})
    assert trail.verify_integrity() is True
    assert len(trail.get_trail()) == 2


def test_audit_trail_tamper_detection():
    """Test that audit trail detects tampering."""
    trail = AuditTrail(secret_key="test-key-for-tamper-detection")
    trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value1"})
    trail.log("test-actor", "test-tier", "TEST_EVENT", {"data": "value2"})
    # Tamper with the first entry
    trail.logs[0]["current_hash"] = "TAMPERED_HASH"
    assert trail.verify_integrity() is False


def test_cli_batch_path_traversal_protection():
    """Test that batch command blocks path traversal attempts."""
    result = main(["batch", "-i", "../etc/passwd", "-o", "results.csv"])
    assert result == 1


def test_cli_batch_missing_file():
    """Test that batch command handles missing input file."""
    result = main(["batch", "-i", "nonexistent_file.csv", "-o", "results.csv"])
    assert result == 1


def test_cli_audit_with_various_statuses():
    """Test CLI audit with different status descriptors."""
    assert main(["audit", "--status", "NOMINAL"]) == 0
    assert main(["audit", "--status", "DISCORDANT_ANOMALY"]) == 0
    assert main(["audit", "--status", "MUTANT_VARIANT"]) == 0
    assert main(["audit", "--critical"]) == 0


def test_worker_no_alerts_on_normal_input():
    """Test that workers produce no alerts for normal inputs."""
    p = SystemTaskPayload(
        task_id="NORMAL-01",
        target_identifier="KEY-NORMAL",
        primary_metric=10.0,
        secondary_metric=5.0,
        status_descriptor="NOMINAL",
        is_critical_flag=False,
    )
    assert len(InvariantQCWorker.evaluate(p)) == 0
    assert len(SafetyEscalationWorker.evaluate(p)) == 0
    assert len(ProtocolConformanceWorker.evaluate(p)) == 0

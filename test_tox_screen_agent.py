import pytest
from tox_screen_agent import ImmunoassayCrossReactivityAgent, PrescriptionReconcilerAgent, LCMSConfirmatoryPlannerAgent, ToxCoordinator, main


def test_sub_agents():
    a1 = ImmunoassayCrossReactivityAgent()
    alerts1 = a1.evaluate({"metric_primary": 35.0})
    assert len(alerts1) == 1

    a2 = PrescriptionReconcilerAgent()
    alerts2 = a2.evaluate({"critical_flag": True})
    assert len(alerts2) == 1

    a3 = LCMSConfirmatoryPlannerAgent()
    alerts3 = a3.evaluate({"status_text": "DISCORDANT_FINDING"})
    assert len(alerts3) == 1


def test_sub_agents_no_alerts_on_normal():
    """Test that sub-agents produce no alerts for normal inputs."""
    a1 = ImmunoassayCrossReactivityAgent()
    assert len(a1.evaluate({"metric_primary": 10.0})) == 0

    a2 = PrescriptionReconcilerAgent()
    assert len(a2.evaluate({"critical_flag": False, "metric_secondary": 5.0})) == 0

    a3 = LCMSConfirmatoryPlannerAgent()
    assert len(a3.evaluate({"status_text": "NORMAL"})) == 0


def test_coordinator():
    coord = ToxCoordinator()
    dossier = coord.audit_case({"case_id": "TEST-100", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert dossier["overall_status"] == "CONCORDANT_NORMAL"
    assert dossier["total_alerts"] == 0

    ans = coord.query_assistant("What are the guidelines?")
    assert "guidelines" in ans or "standards" in ans


def test_coordinator_case_registry():
    """Test that coordinator properly registers cases."""
    coord = ToxCoordinator()
    dossier = coord.audit_case({"case_id": "REG-001", "metric_primary": 10.0, "metric_secondary": 2.0})
    assert "REG-001" in coord.case_registry
    assert coord.case_registry["REG-001"]["overall_status"] == "CONCORDANT_NORMAL"


def test_cli():
    assert main(["audit", "--case-id", "CLI-01"]) == 0
    assert main(["chat", "What", "is", "the", "system", "status?"]) == 0


def test_cli_batch_path_traversal():
    """Test that CLI batch command blocks path traversal."""
    assert main(["batch", "-i", "../../../etc/passwd", "-o", "results.csv"]) == 1


def test_cli_batch_missing_file():
    """Test that CLI batch command handles missing input file."""
    assert main(["batch", "-i", "nonexistent.csv", "-o", "results.csv"]) == 1


def test_domain_registry():
    from tox_screen_agent import DomainKnowledgeRegistry
    assert DomainKnowledgeRegistry.ZERO_PHI_COMPLIANCE is True
    assert "PRO" in DomainKnowledgeRegistry.SYSTEM_VERSION

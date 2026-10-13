"""Security and validation regression tests."""
import math
import pytest
from pydantic import ValidationError
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from cli import main as enterprise_main
from tox_screen_agent import main as standalone_main
from toxicology_drug_screen_agent.cli import main as clinical_main

def make_trail():
    trail = AuditTrail(secret_key="test-only-key")
    trail.log("actor", "supervisor", "EVENT", {"status": "SUCCESS"})
    trail.log("actor", "supervisor", "EVENT", {"status": "SUCCESS"})
    return trail

@pytest.mark.parametrize("field", ["timestamp", "actor", "event_type", "payload_hash", "current_hash"])
def test_tampering_detected(field):
    trail = make_trail()
    trail.logs[-1][field] = "tampered"
    assert trail.verify_integrity() is False

def test_export_is_snapshot():
    trail = make_trail()
    trail.get_trail()[0]["actor"] = "tampered"
    assert trail.verify_integrity() is True

def test_sensitive_actor_rejected():
    trail = AuditTrail(secret_key="test-only-key")
    with pytest.raises(SecurityException):
        trail.log("test@example.com", "supervisor", "EVENT", {"status": "SUCCESS"})
    assert trail.get_trail() == []

@pytest.mark.parametrize("value", [math.inf, -math.inf, math.nan])
def test_invalid_floats_rejected(value):
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="S", primary_metric=value)
    with pytest.raises(ValidationError):
        SystemTaskPayload(task_id="T", target_identifier="S", primary_metric=1, secondary_metric=value)

@pytest.mark.parametrize("command,args", [
    (enterprise_main, ["audit", "--primary", "inf"]),
    (standalone_main, ["audit", "--primary", "nan"]),
    (clinical_main, ["audit", "--secondary", "inf"])
])
def test_cli_rejects_nonfinite(command, args):
    assert command(args) == 1

@pytest.mark.parametrize("command", [enterprise_main, standalone_main, clinical_main])
def test_sibling_directory_not_allowed(command, tmp_path, monkeypatch):
    work = tmp_path / "work"
    sibling = tmp_path / "work-other"
    work.mkdir()
    sibling.mkdir()
    (sibling / "test.csv").write_text("case_id\nX\n")
    monkeypatch.chdir(work)
    assert command(["batch", "-i", "../work-other/test.csv", "-o", "result.csv"]) == 1

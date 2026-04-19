"""Contract tests for the persistent GSD task registry."""

from __future__ import annotations

import json
from pathlib import Path


def test_gsd_task_registry_files_exist() -> None:
    schema_path = Path(".gsd/task-registry.schema.json")
    registry_path = Path(".gsd/task-registry.json")

    assert schema_path.exists()
    assert registry_path.exists()


def test_gsd_task_registry_schema_has_task_record_definition() -> None:
    schema = json.loads(
        Path(".gsd/task-registry.schema.json").read_text(encoding="utf-8")
    )

    assert schema["title"] == "PyRME Task Registry"
    assert "$defs" in schema
    assert "task_record" in schema["$defs"]
    assert "required" in schema["$defs"]["task_record"]


def test_gsd_task_registry_contains_required_shape() -> None:
    registry = json.loads(Path(".gsd/task-registry.json").read_text(encoding="utf-8"))

    assert registry["version"] == 1
    assert registry["project"] == "remeres-map-editor-redux"
    assert isinstance(registry["tasks"], list)
    assert registry["tasks"]

    task_ids = {task["id"] for task in registry["tasks"]}
    assert {
        "GSD-RUNTIME-NODE22",
        "GSD-RUNTIME-LOCAL-HOME",
        "CODEX-SUPERPOWERS-GSD-CONTRACT",
        "GSD-TASK-REGISTRY",
        "TIER2-DIALOGS-DOCKS",
        "TIER2-QSS-NORMALIZATION",
        "M2-RUST-FOUNDATION",
    } <= task_ids

    for task in registry["tasks"]:
        assert task["id"]
        assert task["title"]
        assert task["status"] in {
            "planned",
            "in_progress",
            "implemented",
            "verified",
            "blocked",
            "deferred",
        }
        assert task["recorded_at"]
        assert task["updated_at"]
        assert "scope" in task
        assert "done_criteria" in task
        assert "verification" in task
        assert task["verification"]["status"] in {"not_run", "partial", "passed"}

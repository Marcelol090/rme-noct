from __future__ import annotations

import hashlib
import os
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable

ROOT = Path(__file__).resolve().parents[2]
GSD_LOADER = ROOT / "node_modules" / "gsd-pi" / "dist" / "loader.js"
GSD_PATCHER = ROOT / "scripts" / "patch-gsd-pi.mjs"
GSD_CLI = ROOT / "node_modules" / "gsd-pi" / "dist" / "cli.js"
GSD_HEADLESS = ROOT / "node_modules" / "gsd-pi" / "dist" / "headless.js"
GSD_RPC_CLIENT = (
    ROOT
    / "node_modules"
    / "gsd-pi"
    / "packages"
    / "pi-coding-agent"
    / "dist"
    / "modes"
    / "rpc"
    / "rpc-client.js"
)


def _wait_for(predicate: Callable[[], bool], timeout: float = 30.0, interval: float = 0.25) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def _read_log(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_patcher_replaces_static_pi_coding_agent_barrels_with_lazy_loaders() -> None:
    subprocess.run(["node", str(GSD_PATCHER)], cwd=ROOT, check=True)

    cli_content = GSD_CLI.read_text(encoding="utf-8")
    headless_content = GSD_HEADLESS.read_text(encoding="utf-8")

    assert "from '@gsd/pi-coding-agent'" not in cli_content
    assert "from '@gsd/pi-coding-agent'" not in headless_content
    assert (
        "// Lazy-load the print/RPC API without importing the full pi-coding-agent barrel."
        in cli_content
    )
    assert "async function loadPiAgentPrintApi()" in cli_content
    print_mode_branch = cli_content.index("if (isPrintMode) {")
    top_level_cli_bootstrap = cli_content[:print_mode_branch]
    assert "await loadPiAgentApi()" not in top_level_cli_bootstrap
    assert "loadPiAgentApi()" not in cli_content
    assert (
        "// Lazy-load only the RPC/session modules we need instead of the pi-coding-agent barrel."
        in headless_content
    )
    assert "async function loadPiAgentRpcClient()" in headless_content
    assert "async function loadPiAgentSessionManager()" in headless_content


def test_patcher_is_idempotent_for_gsd_entrypoints_and_rpc_client() -> None:
    subprocess.run(["node", str(GSD_PATCHER)], cwd=ROOT, check=True)
    patched_files = [GSD_CLI, GSD_HEADLESS, GSD_RPC_CLIENT]
    hashes_after_first_run = {path: _sha256(path) for path in patched_files}

    subprocess.run(["node", str(GSD_PATCHER)], cwd=ROOT, check=True)

    assert {path: _sha256(path) for path in patched_files} == hashes_after_first_run
    rpc_client_content = GSD_RPC_CLIENT.read_text(encoding="utf-8")
    assert rpc_client_content.count("[rpc-client] spawn: node") == 1


def test_headless_new_milestone_materializes_canonical_skeleton_before_prompt(
    tmp_path: Path,
) -> None:
    project_root = tmp_path / "repo"
    project_root.mkdir()

    subprocess.run(["git", "init", "-q"], cwd=project_root, check=True)

    env = os.environ.copy()
    env["GSD_HOME"] = str(project_root / ".gsd")

    subprocess.run(
        ["node", str(GSD_PATCHER)],
        cwd=ROOT,
        env=env,
        check=True,
        stdout=subprocess.DEVNULL,
    )

    log_path = project_root / "headless.stderr.log"
    expected_paths = [
        project_root / ".gsd" / "PROJECT.md",
        project_root / ".gsd" / "REQUIREMENTS.md",
        project_root / ".gsd" / "DECISIONS.md",
        project_root / ".gsd" / "QUEUE.md",
        project_root / ".gsd" / "STATE.md",
    ]

    proc = None
    log_file = log_path.open("w", encoding="utf-8")
    try:
        proc = subprocess.Popen(
            [
                "node",
                str(GSD_LOADER),
                "headless",
                "new-milestone",
                "--context-text",
                "Debug milestone materialization",
            ],
            cwd=project_root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=log_file,
        )

        def skeleton_ready() -> bool:
            if proc and proc.poll() is not None:
                return True
            milestone_dirs = [
                path
                for path in (project_root / ".gsd" / "milestones").glob("M*")
                if path.is_dir()
            ]
            return all(path.exists() for path in expected_paths) and any(
                path.is_dir()
                and (path / "slices").is_dir()
                and (path / f"{path.name}-CONTEXT.md").is_file()
                for path in milestone_dirs
            )

        assert _wait_for(skeleton_ready, timeout=30.0), _read_log(log_path)

        if proc and proc.poll() is not None and not all(path.exists() for path in expected_paths):
            pytest.fail(
                "headless exited before the canonical skeleton was materialized:\n"
                f"{_read_log(log_path)}"
            )

        project_content = (project_root / ".gsd" / "PROJECT.md").read_text(encoding="utf-8")
        requirements_content = (project_root / ".gsd" / "REQUIREMENTS.md").read_text(
            encoding="utf-8",
        )
        decisions_content = (project_root / ".gsd" / "DECISIONS.md").read_text(encoding="utf-8")
        queue_content = (project_root / ".gsd" / "QUEUE.md").read_text(encoding="utf-8")
        state_content = (project_root / ".gsd" / "STATE.md").read_text(encoding="utf-8")

        milestone_dirs = [
            path
            for path in (project_root / ".gsd" / "milestones").iterdir()
            if path.is_dir() and path.name.startswith("M")
        ]
        assert milestone_dirs, _read_log(log_path)
        milestone_dir = milestone_dirs[0]
        assert (milestone_dir / "slices").is_dir()
        milestone_context = milestone_dir / f"{milestone_dir.name}-CONTEXT.md"
        assert milestone_context.is_file()

        assert "## Milestone Sequence" in project_content
        assert "| ID | Title | Status |" in project_content
        assert "## Active" in requirements_content
        assert "## Traceability" in requirements_content
        assert (
            "| # | When | Scope | Decision | Choice | Rationale | Revisable? | Made By |"
            in decisions_content
        )
        assert "# Queue" in queue_content
        assert f"# {milestone_dir.name}: Seeded milestone" in milestone_context.read_text(
            encoding="utf-8",
        )
        assert f"**Active Milestone:** {milestone_dir.name}: Seeded milestone" in state_content
        assert "**Phase:** pre-planning" in state_content
        assert "**Next Action:** Plan milestone" in state_content
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=10)
        log_file.close()

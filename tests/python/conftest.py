"""Pytest configuration for Qt widget tests."""

from __future__ import annotations

import os
import shutil
import sys
import uuid
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def settings_workspace():
    workspace = ROOT / ".tmp-tests" / f"settings-{uuid.uuid4().hex}"
    workspace.mkdir(parents=True, exist_ok=True)
    try:
        yield workspace
    finally:
        shutil.rmtree(workspace, ignore_errors=True)

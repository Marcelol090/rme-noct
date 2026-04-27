"""Tests for Welcome Dialog data models and startup components.

TDD: RED phase — all tests written before implementation.
"""

from __future__ import annotations

import pytest

from pyrme.ui.models.startup_models import (
    StartupCompatibilityStatus,
    StartupConfiguredClientEntry,
    StartupInfoField,
    StartupLoadRequest,
    StartupMapPeekResult,
    StartupRecentMapEntry,
)


# ── T07: Data Models ──────────────────────────────────────────────────


class TestStartupCompatibilityStatus:
    """Verify enum has all 5 states matching legacy."""

    def test_has_compatible(self):
        assert StartupCompatibilityStatus.COMPATIBLE is not None

    def test_has_force_required(self):
        assert StartupCompatibilityStatus.FORCE_REQUIRED is not None

    def test_has_forced(self):
        assert StartupCompatibilityStatus.FORCED is not None

    def test_has_map_error(self):
        assert StartupCompatibilityStatus.MAP_ERROR is not None

    def test_has_missing_selection(self):
        assert StartupCompatibilityStatus.MISSING_SELECTION is not None

    def test_exactly_five_members(self):
        assert len(StartupCompatibilityStatus) == 5


class TestStartupRecentMapEntry:
    """Verify map entry data model."""

    def test_path_stored(self):
        entry = StartupRecentMapEntry(path="/maps/test.otbm")
        assert entry.path == "/maps/test.otbm"

    def test_modified_label_default_empty(self):
        entry = StartupRecentMapEntry(path="/maps/test.otbm")
        assert entry.modified_label == ""

    def test_ephemeral_default_false(self):
        entry = StartupRecentMapEntry(path="/maps/test.otbm")
        assert entry.ephemeral is False

    def test_ephemeral_set(self):
        entry = StartupRecentMapEntry(path="/maps/test.otbm", ephemeral=True)
        assert entry.ephemeral is True


class TestStartupConfiguredClientEntry:
    """Verify client entry data model."""

    def test_name_stored(self):
        entry = StartupConfiguredClientEntry(name="Tibia 12.86")
        assert entry.name == "Tibia 12.86"

    def test_otb_versions(self):
        entry = StartupConfiguredClientEntry(
            name="Tibia 12.86",
            otb_major=3,
            otb_minor=57,
        )
        assert entry.otb_major == 3
        assert entry.otb_minor == 57

    def test_version_id(self):
        entry = StartupConfiguredClientEntry(
            name="Tibia 12.86",
            version_id="1286",
        )
        assert entry.version_id == "1286"


class TestStartupMapPeekResult:
    """Verify peek result stub."""

    def test_default_no_error(self):
        result = StartupMapPeekResult()
        assert result.has_error is False

    def test_error_state(self):
        result = StartupMapPeekResult(has_error=True, error_message="corrupt")
        assert result.has_error is True
        assert result.error_message == "corrupt"

    def test_version_fields(self):
        result = StartupMapPeekResult(
            items_major_version=3,
            items_minor_version=57,
        )
        assert result.items_major_version == 3
        assert result.items_minor_version == 57

    def test_dimensions(self):
        result = StartupMapPeekResult(map_width=32000, map_height=32000)
        assert result.map_width == 32000
        assert result.map_height == 32000


class TestStartupLoadRequest:
    """Verify load request model."""

    def test_required_fields(self):
        req = StartupLoadRequest(
            map_path="/maps/test.otbm",
            client_version_id="1286",
        )
        assert req.map_path == "/maps/test.otbm"
        assert req.client_version_id == "1286"

    def test_force_default_false(self):
        req = StartupLoadRequest(
            map_path="/maps/test.otbm",
            client_version_id="1286",
        )
        assert req.force_client_mismatch is False

    def test_force_set(self):
        req = StartupLoadRequest(
            map_path="/maps/test.otbm",
            client_version_id="1286",
            force_client_mismatch=True,
        )
        assert req.force_client_mismatch is True


class TestStartupInfoField:
    """Verify info field model."""

    def test_label_value(self):
        field = StartupInfoField(label="OTBM Version", value="3.2")
        assert field.label == "OTBM Version"
        assert field.value == "3.2"

    def test_mono_font_default_false(self):
        field = StartupInfoField(label="Name", value="Test")
        assert field.use_mono_font is False

    def test_mono_font_set(self):
        field = StartupInfoField(
            label="Version", value="12.86", use_mono_font=True
        )
        assert field.use_mono_font is True

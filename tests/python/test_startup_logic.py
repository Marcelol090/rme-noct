"""Tests for Welcome Dialog compatibility status engine.

T11: Compatibility status computation + message generation.
Direct behavioral parity with legacy WelcomeDialog::GetCompatibilityStatus()
and WelcomeDialog::BuildCompatibilityMessage().
"""

from __future__ import annotations

import pytest

from pyrme.ui.models.startup_logic import (
    build_client_info_fields,
    build_compatibility_message,
    build_map_info_fields,
    compute_compatibility_status,
)
from pyrme.ui.models.startup_models import (
    StartupCompatibilityStatus,
    StartupConfiguredClientEntry,
    StartupMapPeekResult,
)

# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def matching_map():
    return StartupMapPeekResult(
        map_name="forgotten_city",
        items_major_version=3,
        items_minor_version=57,
        map_width=32000,
        map_height=32000,
        description="Rain city rework",
    )


@pytest.fixture
def matching_client():
    return StartupConfiguredClientEntry(
        name="Tibia 12.86",
        version_id="1286",
        client_path="C:/Tibia/1286",
        otb_major=3,
        otb_minor=57,
    )


@pytest.fixture
def mismatched_client():
    return StartupConfiguredClientEntry(
        name="Tibia 10.98",
        version_id="1098",
        client_path="C:/Tibia/1098",
        otb_major=3,
        otb_minor=42,
    )


@pytest.fixture
def error_map():
    return StartupMapPeekResult(has_error=True, error_message="Corrupt OTBM")


# ── T11: Status Computation ──────────────────────────────────────────


class TestComputeCompatibilityStatus:
    """Legacy: WelcomeDialog::GetCompatibilityStatus()."""

    def test_compatible_when_versions_match(self, matching_map, matching_client):
        status = compute_compatibility_status(matching_map, matching_client)
        assert status == StartupCompatibilityStatus.COMPATIBLE

    def test_force_required_when_mismatch(self, matching_map, mismatched_client):
        status = compute_compatibility_status(matching_map, mismatched_client)
        assert status == StartupCompatibilityStatus.FORCE_REQUIRED

    def test_forced_when_mismatch_and_force(self, matching_map, mismatched_client):
        status = compute_compatibility_status(
            matching_map, mismatched_client, force_load=True
        )
        assert status == StartupCompatibilityStatus.FORCED

    def test_missing_when_no_map(self, matching_client):
        status = compute_compatibility_status(None, matching_client)
        assert status == StartupCompatibilityStatus.MISSING_SELECTION

    def test_missing_when_no_client(self, matching_map):
        status = compute_compatibility_status(matching_map, None)
        assert status == StartupCompatibilityStatus.MISSING_SELECTION

    def test_missing_when_both_none(self):
        status = compute_compatibility_status(None, None)
        assert status == StartupCompatibilityStatus.MISSING_SELECTION

    def test_map_error(self, error_map, matching_client):
        status = compute_compatibility_status(error_map, matching_client)
        assert status == StartupCompatibilityStatus.MAP_ERROR


# ── T11: Message Generation ──────────────────────────────────────────


class TestBuildCompatibilityMessage:
    """Legacy: WelcomeDialog::BuildCompatibilityMessage()."""

    def test_compatible_message(self, matching_map, matching_client):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.COMPATIBLE,
            matching_map, matching_client,
        )
        assert "matches" in msg.lower()
        assert "ready" in msg.lower()

    def test_force_required_message(self, matching_map, mismatched_client):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.FORCE_REQUIRED,
            matching_map, mismatched_client,
        )
        assert "3.57" in msg  # map version
        assert "3.42" in msg  # client version
        assert "Force Load" in msg

    def test_forced_message(self, matching_map, mismatched_client):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.FORCED,
            matching_map, mismatched_client,
        )
        assert "mismatch" in msg.lower()
        assert "ignored" in msg.lower()

    def test_no_maps_message(self, matching_map, matching_client):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.MISSING_SELECTION,
            matching_map, matching_client,
            has_maps=False,
        )
        assert "no recent maps" in msg.lower()

    def test_no_map_selected_message(self):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.MISSING_SELECTION,
            map_info=None,
        )
        assert "select a map" in msg.lower()

    def test_no_client_selected_message(self, matching_map):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.MISSING_SELECTION,
            map_info=matching_map,
            client=None,
        )
        assert "select a configured client" in msg.lower()

    def test_map_error_message(self, error_map, matching_client):
        msg = build_compatibility_message(
            StartupCompatibilityStatus.MAP_ERROR,
            error_map, matching_client,
        )
        assert "could not be previewed" in msg.lower()


# ── T11: Info Field Builders ─────────────────────────────────────────


class TestBuildMapInfoFields:
    def test_no_map_shows_status(self):
        fields = build_map_info_fields(None)
        assert len(fields) == 1
        assert "no map" in fields[0].value.lower()

    def test_error_map_shows_error(self, error_map):
        fields = build_map_info_fields(error_map)
        assert len(fields) == 1
        assert "Corrupt OTBM" in fields[0].value

    def test_valid_map_shows_all_fields(self, matching_map):
        fields = build_map_info_fields(matching_map)
        labels = [f.label for f in fields]
        assert "MAP NAME" in labels
        assert "ITEMS VERSION" in labels
        assert "DIMENSIONS" in labels
        assert "DESCRIPTION" in labels

    def test_version_uses_mono_font(self, matching_map):
        fields = build_map_info_fields(matching_map)
        version_field = next(f for f in fields if f.label == "ITEMS VERSION")
        assert version_field.use_mono_font is True

    def test_dimensions_format(self, matching_map):
        fields = build_map_info_fields(matching_map)
        dim_field = next(f for f in fields if f.label == "DIMENSIONS")
        assert "32000" in dim_field.value


class TestBuildClientInfoFields:
    def test_no_client_shows_status(self):
        fields = build_client_info_fields(None)
        assert len(fields) == 1
        assert "no client" in fields[0].value.lower()

    def test_valid_client_shows_all_fields(self, matching_client):
        fields = build_client_info_fields(matching_client)
        labels = [f.label for f in fields]
        assert "CLIENT" in labels
        assert "VERSION ID" in labels
        assert "OTB VERSION" in labels
        assert "PATH" in labels

    def test_otb_version_uses_mono_font(self, matching_client):
        fields = build_client_info_fields(matching_client)
        otb_field = next(f for f in fields if f.label == "OTB VERSION")
        assert otb_field.use_mono_font is True

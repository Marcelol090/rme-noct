"""Compatibility status engine for the Welcome Dialog.

Port of legacy WelcomeDialog::GetCompatibilityStatus() and
WelcomeDialog::BuildCompatibilityMessage().
"""

from __future__ import annotations

from pyrme.ui.models.startup_models import (
    StartupCompatibilityStatus,
    StartupConfiguredClientEntry,
    StartupInfoField,
    StartupMapPeekResult,
)


def compute_compatibility_status(
    map_info: StartupMapPeekResult | None,
    client: StartupConfiguredClientEntry | None,
    force_load: bool = False,
) -> StartupCompatibilityStatus:
    """Compute compatibility status between map and client.

    Direct port of legacy WelcomeDialog::GetCompatibilityStatus().
    """
    if map_info is None or client is None:
        return StartupCompatibilityStatus.MISSING_SELECTION
    if map_info.has_error:
        return StartupCompatibilityStatus.MAP_ERROR

    matches = (
        client.otb_major == map_info.items_major_version
        and client.otb_minor == map_info.items_minor_version
    )
    if matches:
        return StartupCompatibilityStatus.COMPATIBLE
    return (
        StartupCompatibilityStatus.FORCED
        if force_load
        else StartupCompatibilityStatus.FORCE_REQUIRED
    )


def build_compatibility_message(
    status: StartupCompatibilityStatus,
    map_info: StartupMapPeekResult | None = None,
    client: StartupConfiguredClientEntry | None = None,
    has_maps: bool = True,
) -> str:
    """Build human-readable compatibility message.

    Direct port of legacy WelcomeDialog::BuildCompatibilityMessage().
    """
    if not has_maps:
        return "No recent maps yet. Browse for a map or start a new one."
    if map_info is None:
        return "Select a map to preview its header information."
    if map_info.has_error:
        return (
            "The selected map could not be previewed. "
            "Loading is disabled until a valid OTBM is selected."
        )
    if client is None:
        return "Select a configured client to compare against the map header."

    if status == StartupCompatibilityStatus.COMPATIBLE:
        return "Selected client matches the map items version. Load is ready."
    if status == StartupCompatibilityStatus.FORCED:
        return (
            "Client mismatch is being ignored. "
            "The map will load with the selected client assets."
        )
    if status == StartupCompatibilityStatus.FORCE_REQUIRED:
        return (
            f"Map header expects items {map_info.items_major_version}."
            f"{map_info.items_minor_version} while the selected client "
            f"provides {client.otb_major}.{client.otb_minor}. "
            f"Enable Force Load to continue anyway."
        )
    if status == StartupCompatibilityStatus.MAP_ERROR:
        return (
            "The selected map could not be previewed. "
            "Loading is disabled until a valid OTBM is selected."
        )
    return "Select both a map and a configured client to continue."


def build_map_info_fields(
    peek: StartupMapPeekResult | None,
) -> list[StartupInfoField]:
    """Build info fields from OTBM peek result."""
    if peek is None:
        return [StartupInfoField(label="STATUS", value="No map selected")]
    if peek.has_error:
        return [
            StartupInfoField(
                label="ERROR", value=peek.error_message or "Cannot read map"
            )
        ]
    return [
        StartupInfoField(label="MAP NAME", value=peek.map_name or "Unnamed"),
        StartupInfoField(
            label="ITEMS VERSION",
            value=f"{peek.items_major_version}.{peek.items_minor_version}",
            use_mono_font=True,
        ),
        StartupInfoField(
            label="DIMENSIONS",
            value=f"{peek.map_width} × {peek.map_height}",
            use_mono_font=True,
        ),
        StartupInfoField(
            label="DESCRIPTION",
            value=peek.description or "No description",
        ),
    ]


def build_client_info_fields(
    client: StartupConfiguredClientEntry | None,
) -> list[StartupInfoField]:
    """Build info fields from client entry."""
    if client is None:
        return [StartupInfoField(label="STATUS", value="No client selected")]
    return [
        StartupInfoField(label="CLIENT", value=client.name),
        StartupInfoField(
            label="VERSION ID",
            value=client.version_id or "N/A",
            use_mono_font=True,
        ),
        StartupInfoField(
            label="OTB VERSION",
            value=f"{client.otb_major}.{client.otb_minor}",
            use_mono_font=True,
        ),
        StartupInfoField(label="PATH", value=client.client_path or "N/A"),
    ]

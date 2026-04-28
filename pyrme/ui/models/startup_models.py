"""Data models for the Welcome Dialog startup screen.

Behavioral parity with legacy WelcomeDialog (welcome_dialog.h).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional


class StartupCompatibilityStatus(Enum):
    """Compatibility status between selected map and client."""

    COMPATIBLE = auto()
    FORCE_REQUIRED = auto()
    FORCED = auto()
    MAP_ERROR = auto()
    MISSING_SELECTION = auto()


@dataclass
class StartupRecentMapEntry:
    """A recent map file entry in the startup list."""

    path: str
    modified_label: str = ""
    ephemeral: bool = False


@dataclass
class StartupConfiguredClientEntry:
    """A configured client entry in the startup list."""

    name: str
    client_path: str = ""
    version_id: str = ""
    otb_major: int = 0
    otb_minor: int = 0


@dataclass
class StartupMapPeekResult:
    """Stub for OTBM header peek result.

    Will be replaced by real Rust bridge later.
    """

    map_name: str = ""
    map_width: int = 0
    map_height: int = 0
    items_major_version: int = 0
    items_minor_version: int = 0
    description: str = ""
    has_error: bool = False
    error_message: str = ""


@dataclass
class StartupLoadRequest:
    """Request to load a map with a specific client."""

    map_path: str
    client_version_id: str
    force_client_mismatch: bool = False


@dataclass
class StartupInfoField:
    """A single key-value field for the info panel."""

    label: str
    value: str
    use_mono_font: bool = False

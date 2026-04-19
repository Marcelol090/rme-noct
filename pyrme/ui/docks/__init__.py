"""Package for PyRME dock panels."""

from .brush_palette import BrushPaletteDock
from .minimap import MinimapDock
from .properties import PropertiesDock
from .waypoints import WaypointEntry, WaypointsDock

__all__ = [
    "BrushPaletteDock",
    "MinimapDock",
    "PropertiesDock",
    "WaypointEntry",
    "WaypointsDock",
]

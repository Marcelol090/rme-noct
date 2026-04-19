"""Package for PyRME dock panels."""

from .brush_palette import BrushPaletteDock
from .ingame_preview import IngamePreviewDock
from .minimap import MinimapDock
from .properties import PropertiesDock
from .tool_options import ToolOptionsDock
from .waypoints import WaypointEntry, WaypointsDock

__all__ = [
    "BrushPaletteDock",
    "IngamePreviewDock",
    "MinimapDock",
    "PropertiesDock",
    "ToolOptionsDock",
    "WaypointEntry",
    "WaypointsDock",
]

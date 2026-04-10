from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from pyrme.ui.dialogs.map_properties import MapPropertiesState

if TYPE_CHECKING:
    from pyrme.ui.canvas_host import CanvasWidgetProtocol


@dataclass(slots=True)
class MapDocumentState:
    name: str = "Untitled"
    is_dirty: bool = False
    properties: MapPropertiesState = field(default_factory=MapPropertiesState)


@dataclass(slots=True)
class EditorContext:
    document_id: str = field(default_factory=lambda: f"map-{uuid4().hex}")
    map_document: MapDocumentState = field(default_factory=MapDocumentState)
    editor_mode: str = "drawing"


@dataclass(frozen=True, slots=True)
class ShellStateSnapshot:
    current_x: int
    current_y: int
    current_z: int
    previous_position: tuple[int, int, int] | None
    zoom_percent: int
    show_grid_enabled: bool
    ghost_higher_enabled: bool
    show_lower_enabled: bool


@dataclass(slots=True)
class EditorViewRecord:
    canvas: CanvasWidgetProtocol
    editor_context: EditorContext
    shell_state: ShellStateSnapshot

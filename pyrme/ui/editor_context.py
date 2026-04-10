from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from pyrme.editor.model import EditorModel, MapModel, MapPropertiesState

if TYPE_CHECKING:
    from pyrme.ui.canvas_host import CanvasWidgetProtocol


@dataclass(slots=True)
class MapDocumentState:
    editor: EditorModel = field(default_factory=EditorModel)

    @property
    def map_model(self) -> MapModel:
        return self.editor.map_model

    @property
    def name(self) -> str:
        return self.map_model.name

    @name.setter
    def name(self, value: str) -> None:
        self.map_model.name = value

    @property
    def is_dirty(self) -> bool:
        return self.map_model.is_dirty

    @is_dirty.setter
    def is_dirty(self, value: bool) -> None:
        self.map_model.is_dirty = value

    @property
    def properties(self) -> MapPropertiesState:
        return self.map_model.properties

    @properties.setter
    def properties(self, value: MapPropertiesState) -> None:
        self.map_model.update_properties(value)

    def update_properties(self, value: MapPropertiesState) -> bool:
        return self.map_model.update_properties(value)


@dataclass(slots=True)
class EditorViewportState:
    center_x: int = 32000
    center_y: int = 32000
    floor: int = 7


@dataclass(slots=True)
class MinimapViewportState:
    center_x: int = 32000
    center_y: int = 32000
    zoom_percent: int = 100


@dataclass(slots=True)
class EditorSessionState:
    document: MapDocumentState = field(default_factory=MapDocumentState)
    mode: str = "drawing"
    active_brush_id: str | None = None
    active_item_id: int | None = None

    @property
    def editor(self) -> EditorModel:
        return self.document.editor


@dataclass(slots=True)
class EditorContext:
    document_id: str = field(default_factory=lambda: f"map-{uuid4().hex}")
    session: EditorSessionState = field(default_factory=EditorSessionState)


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
    viewport: EditorViewportState = field(default_factory=EditorViewportState)
    minimap_viewport: MinimapViewportState = field(default_factory=MinimapViewportState)

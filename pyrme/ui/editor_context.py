from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from uuid import uuid4

from pyrme.editor import EditorModel, MapModel
from pyrme.ui.viewport import EditorViewport

if TYPE_CHECKING:
    from pyrme.ui.canvas_host import CanvasWidgetProtocol


@dataclass(slots=True)
class MapDocumentState:
    editor: EditorModel = field(default_factory=EditorModel)
    path: str | None = None
    persistence_handle: object | None = None

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


@dataclass(slots=True)
class EditorSessionState:
    document: MapDocumentState = field(default_factory=MapDocumentState)

    @property
    def editor(self) -> EditorModel:
        return self.document.editor

    @property
    def mode(self) -> str:
        return self.editor.mode

    @mode.setter
    def mode(self, value: str) -> None:
        self.editor.mode = value

    @property
    def active_brush_id(self) -> str | None:
        return self.editor.active_brush_id

    @active_brush_id.setter
    def active_brush_id(self, value: str | None) -> None:
        self.editor.active_brush_id = value

    @property
    def active_item_id(self) -> int | None:
        return self.editor.active_item_id

    @active_item_id.setter
    def active_item_id(self, value: int | None) -> None:
        self.editor.active_item_id = value


@dataclass(slots=True)
class EditorContext:
    document_id: str = field(default_factory=lambda: f"map-{uuid4().hex}")
    session: EditorSessionState = field(default_factory=EditorSessionState)


@dataclass(frozen=True, slots=True)
class ShellStateSnapshot:
    show_grid_enabled: bool
    ghost_higher_enabled: bool
    show_lower_enabled: bool
    view_flags: dict[str, bool] = field(default_factory=dict)
    show_flags: dict[str, bool] = field(default_factory=dict)


@dataclass(slots=True)
class MinimapViewportState:
    center_x: int = 32000
    center_y: int = 32000
    floor: int = 7
    zoom_percent: int = 100


@dataclass(slots=True)
class EditorViewRecord:
    canvas: CanvasWidgetProtocol
    editor_context: EditorContext
    shell_state: ShellStateSnapshot
    viewport: EditorViewport = field(default_factory=EditorViewport)
    minimap_viewport: MinimapViewportState = field(default_factory=MinimapViewportState)

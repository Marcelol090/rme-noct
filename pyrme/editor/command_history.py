from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from pyrme.core_bridge import EditorShellCoreBridge, create_editor_shell_state

TileSnapshotPayload: TypeAlias = tuple[int | None, tuple[int, ...]]  # noqa: UP040
TileCommandPayload: TypeAlias = tuple[  # noqa: UP040
    int,
    int,
    int,
    TileSnapshotPayload | None,
    TileSnapshotPayload | None,
]


@dataclass(slots=True)
class TileCommandHistory:
    bridge: EditorShellCoreBridge = field(default_factory=create_editor_shell_state)

    def record(self, label: str, changes: tuple[TileCommandPayload, ...]) -> bool:
        return self.bridge.record_tile_command(label, changes)

    def can_undo(self) -> bool:
        return self.bridge.can_undo_tile_command()

    def can_redo(self) -> bool:
        return self.bridge.can_redo_tile_command()

    def undo(self) -> tuple[TileCommandPayload, ...]:
        return self.bridge.undo_tile_command()

    def redo(self) -> tuple[TileCommandPayload, ...]:
        return self.bridge.redo_tile_command()

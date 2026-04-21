"""Pure sprite resource diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyrme.rendering.sprite_resolver import SpriteLookupStatus

if TYPE_CHECKING:
    from collections.abc import Iterable

    from pyrme.rendering.frame_sprite_resources import FrameSpriteResource


@dataclass(frozen=True, slots=True)
class SpriteResourceDiagnostics:
    """Counted sprite resource outcomes for renderer diagnostics."""

    total: int
    resolved: int
    missing_item: int
    missing_sprite: int

    def summary(self) -> str:
        if self.total == 0:
            return "Sprite Resources: 0 total (none requested)"
        return (
            f"Sprite Resources: {self.total} total | "
            f"resolved {self.resolved} | "
            f"missing item {self.missing_item} | "
            f"missing sprite {self.missing_sprite}"
        )


def build_sprite_resource_diagnostics(
    resources: Iterable[FrameSpriteResource],
) -> SpriteResourceDiagnostics:
    resolved = 0
    missing_item = 0
    missing_sprite = 0
    total = 0
    for resource in resources:
        total += 1
        if resource.result.status is SpriteLookupStatus.RESOLVED:
            resolved += 1
        elif resource.result.status is SpriteLookupStatus.MISSING_ITEM:
            missing_item += 1
        elif resource.result.status is SpriteLookupStatus.MISSING_SPRITE:
            missing_sprite += 1
    return SpriteResourceDiagnostics(
        total=total,
        resolved=resolved,
        missing_item=missing_item,
        missing_sprite=missing_sprite,
    )

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from pyrme.editor import MapPosition
from pyrme.rendering.frame_sprite_resources import FrameSpriteResource
from pyrme.rendering.sprite_resolver import SpriteResourceResult
from pyrme.rendering.sprite_resource_diagnostics import (
    SpriteResourceDiagnostics,
    build_sprite_resource_diagnostics,
)


def test_sprite_resource_diagnostics_counts_resource_statuses() -> None:
    position = MapPosition(32000, 32000, 7)
    resources = (
        FrameSpriteResource(
            position=position,
            item_id=2148,
            stack_layer=0,
            result=SpriteResourceResult.resolved(
                item_id=2148,
                sprite_id=55,
                pixels=b"coin",
            ),
        ),
        FrameSpriteResource(
            position=position,
            item_id=999_999,
            stack_layer=1,
            result=SpriteResourceResult.missing_item(999_999),
        ),
        FrameSpriteResource(
            position=position,
            item_id=2160,
            stack_layer=2,
            result=SpriteResourceResult.missing_sprite(item_id=2160, sprite_id=99),
        ),
    )

    diagnostics = build_sprite_resource_diagnostics(resources)

    assert diagnostics.total == 3
    assert diagnostics.resolved == 1
    assert diagnostics.missing_item == 1
    assert diagnostics.missing_sprite == 1


def test_sprite_resource_diagnostics_is_immutable() -> None:
    diagnostics = SpriteResourceDiagnostics(
        total=1,
        resolved=1,
        missing_item=0,
        missing_sprite=0,
    )

    with pytest.raises(FrozenInstanceError):
        diagnostics.total = 2  # type: ignore[misc]


def test_sprite_resource_diagnostics_summary_for_empty_resources() -> None:
    diagnostics = SpriteResourceDiagnostics(
        total=0,
        resolved=0,
        missing_item=0,
        missing_sprite=0,
    )

    assert diagnostics.summary() == "Sprite Resources: 0 total (none requested)"


def test_sprite_resource_diagnostics_summary_for_resolved_resources() -> None:
    diagnostics = SpriteResourceDiagnostics(
        total=2,
        resolved=2,
        missing_item=0,
        missing_sprite=0,
    )

    assert (
        diagnostics.summary()
        == "Sprite Resources: 2 total | resolved 2 | missing item 0 | missing sprite 0"
    )


def test_sprite_resource_diagnostics_summary_for_missing_resources() -> None:
    diagnostics = SpriteResourceDiagnostics(
        total=3,
        resolved=1,
        missing_item=1,
        missing_sprite=1,
    )

    assert (
        diagnostics.summary()
        == "Sprite Resources: 3 total | resolved 1 | missing item 1 | missing sprite 1"
    )

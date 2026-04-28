"""Sprite resolver contract tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from pyrme.rendering.sprite_resolver import (
    SpriteItemMetadata,
    SpriteLookupStatus,
    SpriteResourceResolver,
    SpriteResourceResult,
)


def test_resolved_sprite_result_exposes_item_sprite_and_pixels() -> None:
    result = SpriteResourceResult.resolved(
        item_id=2148,
        sprite_id=55,
        pixels=b"rgba",
    )

    assert result.status is SpriteLookupStatus.RESOLVED
    assert result.available is True
    assert result.item_id == 2148
    assert result.sprite_id == 55
    assert result.pixels == b"rgba"
    assert result.reason == ""


def test_missing_item_result_is_explicit_and_has_no_payload() -> None:
    result = SpriteResourceResult.missing_item(999_999)

    assert result.status is SpriteLookupStatus.MISSING_ITEM
    assert result.available is False
    assert result.item_id == 999_999
    assert result.sprite_id is None
    assert result.pixels is None
    assert result.reason == "item id not found"


def test_missing_sprite_result_keeps_item_and_sprite_context() -> None:
    result = SpriteResourceResult.missing_sprite(item_id=2148, sprite_id=55)

    assert result.status is SpriteLookupStatus.MISSING_SPRITE
    assert result.available is False
    assert result.item_id == 2148
    assert result.sprite_id == 55
    assert result.pixels is None
    assert result.reason == "sprite id not found"


def test_sprite_result_is_immutable() -> None:
    result = SpriteResourceResult.missing_item(100)

    with pytest.raises(FrozenInstanceError):
        result.item_id = 200  # type: ignore[misc]


def test_resolver_returns_primary_sprite_id_for_known_item_without_payload() -> None:
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55, 56)),
        }
    )

    result = resolver.resolve_item(2148)

    assert result.status is SpriteLookupStatus.MISSING_SPRITE
    assert result.available is False
    assert result.item_id == 2148
    assert result.sprite_id == 55
    assert result.pixels is None


def test_resolver_reports_missing_item_id() -> None:
    resolver = SpriteResourceResolver(items={})

    result = resolver.resolve_item(999_999)

    assert result.status is SpriteLookupStatus.MISSING_ITEM
    assert result.item_id == 999_999
    assert result.sprite_id is None


def test_resolver_returns_pixels_when_sprite_payload_exists() -> None:
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
        },
        sprites={
            55: b"rgba-pixels",
        },
    )

    result = resolver.resolve_item(2148)

    assert result.status is SpriteLookupStatus.RESOLVED
    assert result.available is True
    assert result.item_id == 2148
    assert result.sprite_id == 55
    assert result.pixels == b"rgba-pixels"


def test_resolver_reports_missing_sprite_when_payload_absent() -> None:
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
        },
        sprites={},
    )

    result = resolver.resolve_item(2148)

    assert result.status is SpriteLookupStatus.MISSING_SPRITE
    assert result.available is False
    assert result.item_id == 2148
    assert result.sprite_id == 55
    assert result.pixels is None


def test_resolver_reuses_cached_result_for_repeated_item_lookup() -> None:
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
        },
        sprites={
            55: b"rgba-pixels",
        },
    )

    first = resolver.resolve_item(2148)
    second = resolver.resolve_item(2148)

    assert first is second


def test_replacing_sources_clears_cached_item_results() -> None:
    resolver = SpriteResourceResolver(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
        },
        sprites={
            55: b"old-pixels",
        },
    )
    old_result = resolver.resolve_item(2148)

    resolver.replace_sources(
        items={
            2148: SpriteItemMetadata(item_id=2148, sprite_ids=(55,)),
        },
        sprites={
            55: b"new-pixels",
        },
    )
    new_result = resolver.resolve_item(2148)

    assert new_result is not old_result
    assert new_result.pixels == b"new-pixels"

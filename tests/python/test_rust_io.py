from __future__ import annotations

import os
import tempfile

from pyrme import rme_core


def test_otb_database_python():
    # We'll use a mock OTB file content
    with tempfile.NamedTemporaryFile(delete=False, suffix=".otb") as tmp:
        # OTBI magic + Root Node
        buf = bytearray(b"OTBI")
        buf.extend([0xFE, 0x00])  # Node Start (0xFE), Type (0x00)
        buf.extend([0, 0, 0, 0])  # Skip 4
        buf.append(0x01)  # ROOT_ATTR_VERSION
        buf.extend([12, 0])  # Length 12
        buf.extend([3, 0, 0, 0])  # Major 3
        buf.extend([0, 0, 0, 0])  # Minor
        buf.extend([0, 0, 0, 0])  # Build

        # Item Node
        buf.extend([0xFE, 0x01])  # Node Start, Type 0x01 (Group)
        buf.extend([0, 0, 0, 0])  # Flags
        buf.append(0x10)  # ITEM_ATTR_SERVERID
        buf.extend([2, 0])  # Length 2
        buf.extend([101, 0])  # ID 101

        buf.append(0xFF)  # Node End
        buf.append(0xFF)  # Node End
        tmp.write(buf)
        tmp_path = tmp.name

    try:
        db = rme_core.OtbDatabase.from_file(tmp_path)
        assert db.item_count() == 1
        item = db.get_item(101)
        assert item.server_id == 101
        assert item.group == 1
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_spr_database_python():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".spr") as tmp:
        buf = bytearray([0, 0, 0, 0])  # Sig
        buf.extend([1, 0])  # Count 1
        offset = 6 + 4
        buf.extend(offset.to_bytes(4, "little"))
        buf.extend([255, 0, 255])  # Color key

        rle = bytearray()
        rle.extend([5, 0])  # 5 transparent
        rle.extend([1, 0])  # 1 colored
        rle.extend([0, 255, 0])  # Green

        buf.extend(len(rle).to_bytes(2, "little"))
        buf.extend(rle)
        tmp.write(buf)
        tmp_path = tmp.name

    try:
        db = rme_core.SprDatabase.from_file(tmp_path)
        assert db.sprite_count() == 1
        pixels = db.get_sprite(1, False)
        assert len(pixels) == 1024 * 4
        # Offset 5 * 4 = 20
        assert pixels[20:24] == bytes([0, 255, 0, 255])
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def test_dat_database_python():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dat") as tmp:
        buf = bytearray([0, 0, 0, 0])  # Sig
        buf.extend([100, 0])  # Items
        buf.extend([0, 0, 0, 0, 0, 0])  # creatures, effects, distances

        # Item 100
        buf.append(0x00)  # Ground
        buf.extend([40, 0])  # Speed 40
        buf.append(0xFF)  # End flags
        buf.extend([1, 1])  # W, H
        buf.extend([1, 1, 1, 1, 1])  # layers, px, py, pz, frames
        buf.extend([55, 0])  # Sprite ID 55

        tmp.write(buf)
        tmp_path = tmp.name

    try:
        db = rme_core.DatDatabase.from_file(tmp_path)
        assert db.item_count() == 1
        item = db.get_item(100)
        assert item.client_id == 100
        assert item.ground is True
        assert item.speed == 40
        assert item.sprite_ids[0] == 55
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

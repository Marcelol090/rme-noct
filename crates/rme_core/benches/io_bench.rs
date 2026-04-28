use criterion::{criterion_group, criterion_main, Criterion};
use rme_core::io::dat::DatDatabase;
use rme_core::io::otb::OtbDatabase;
use rme_core::io::spr::SprDatabase;
use std::hint::black_box;
use std::io::Write;
use tempfile::NamedTempFile;

fn bench_otb_parse(c: &mut Criterion) {
    let mut tmp = NamedTempFile::new().unwrap();
    let buf = bytearray_otb(5000);
    tmp.write_all(&buf).unwrap();
    tmp.flush().unwrap();
    let path = tmp.path().to_str().unwrap().to_string();

    c.bench_function("otb_parse_5k_items", |b| {
        b.iter(|| {
            let db = OtbDatabase::from_file(black_box(path.clone())).unwrap();
            assert!(db.item_count() > 0);
        })
    });
}

fn bench_spr_fetch(c: &mut Criterion) {
    let mut tmp = NamedTempFile::new().unwrap();
    let buf = bytearray_spr(100);
    tmp.write_all(&buf).unwrap();
    tmp.flush().unwrap();
    let path = tmp.path().to_str().unwrap().to_string();
    let db = SprDatabase::from_file(path.clone()).unwrap();

    c.bench_function("spr_fetch_rle_32x32", |b| {
        b.iter(|| {
            let pixels = db.get_sprite(black_box(1), black_box(false)).unwrap();
            assert_eq!(pixels.len(), 4096);
        })
    });
}

fn bench_dat_parse(c: &mut Criterion) {
    let mut tmp = NamedTempFile::new().unwrap();
    let buf = bytearray_dat(5000);
    tmp.write_all(&buf).unwrap();
    tmp.flush().unwrap();
    let path = tmp.path().to_str().unwrap().to_string();

    c.bench_function("dat_parse_5k_items", |b| {
        b.iter(|| {
            let db = DatDatabase::from_file(black_box(path.clone())).unwrap();
            assert!(db.item_count() > 0);
        })
    });
}

fn bytearray_otb(count: usize) -> Vec<u8> {
    let mut buf = Vec::from(b"OTBI");

    let mut root_data = vec![0, 0, 0, 0];
    root_data.push(0x01); // ROOT_ATTR_VERSION
    root_data.extend([12, 0]);
    root_data.extend([3, 0, 0, 0]);
    root_data.extend([0; 8]);

    buf.push(0xFE); // Node Start
    buf.push(0x00); // Root type
    buf.extend(escape_buffer(&root_data));

    for i in 0..count {
        let mut item_data = vec![0, 0, 0, 0];
        item_data.push(0x10); // ATTR_SERVERID
        item_data.extend([2, 0]);
        item_data.extend((i as u16).to_le_bytes());

        buf.push(0xFE);
        buf.push(0x01);
        buf.extend(escape_buffer(&item_data));
        buf.push(0xFF);
    }
    buf.push(0xFF);
    buf
}

fn escape_buffer(data: &[u8]) -> Vec<u8> {
    let mut out = Vec::new();
    for &b in data {
        if b == 0xFE || b == 0xFF || b == 0xFD {
            out.push(0xFD);
        }
        out.push(b);
    }
    out
}

fn bytearray_spr(count: usize) -> Vec<u8> {
    let mut data = Vec::new();
    let mut offsets = Vec::new();

    let start_offset = 6 + (count * 4);
    for _ in 0..count {
        offsets.push((start_offset + data.len()) as u32);
        data.extend([255, 0, 255]); // Color key

        let mut real_rle = Vec::new();
        real_rle.extend(1024u16.to_le_bytes()); // Transparent
        real_rle.extend(0u16.to_le_bytes()); // End

        data.extend((real_rle.len() as u16).to_le_bytes());
        data.extend(real_rle);
    }

    let mut buf = vec![0; 4];
    buf.extend((count as u16).to_le_bytes());
    for offset in offsets {
        buf.extend(offset.to_le_bytes());
    }
    buf.extend(data);
    buf
}

fn bytearray_dat(count: usize) -> Vec<u8> {
    let mut buf = vec![0; 4];
    buf.extend((count as u16).to_le_bytes());
    buf.extend([0u8; 6]); // creatures etc

    // total_items = count + 99. We want count items starting from 100.
    for _ in 0..count {
        buf.push(0x00); // Ground
        buf.extend([10, 0]); // Speed
        buf.push(0xFF); // End flags
        buf.extend([1, 1]); // Dim
        buf.extend([1, 1, 1, 1, 1]); // layers etc
        buf.extend([1, 0]); // Sprite 1
    }
    buf
}

criterion_group!(benches, bench_otb_parse, bench_spr_fetch, bench_dat_parse);
criterion_main!(benches);

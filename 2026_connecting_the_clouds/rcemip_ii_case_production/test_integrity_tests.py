from pathlib import Path

import numpy as np
import xarray as xr

from expected_output import zarr_relpaths
from filesystem_backend import Local_backend
from validate_integrity import (
    check_byte_identical,
    store_has_missing_chunks,
    store_non_finite_count,
)


def write_store(path, data, chunk_size):
    ds = xr.Dataset({'var': ('time', data)}, coords={'time': np.arange(len(data))})
    ds.to_zarr(path, mode='w', consolidated=False, encoding={'var': {'chunks': (chunk_size,)}})


def delete_one_chunk(store_path):
    chunk_files = [p for p in (store_path / 'var' / 'c').rglob('*') if p.is_file()]
    chunk_files[0].unlink()


def test_missing_chunks_false_intact(tmp_path: Path) -> None:
    store_path = tmp_path / 'store.zarr'
    write_store(store_path, np.arange(4, dtype='float32'), chunk_size=2)

    assert store_has_missing_chunks(store_path) is False


def test_missing_chunks_true_after_delete(tmp_path: Path) -> None:
    store_path = tmp_path / 'store.zarr'
    write_store(store_path, np.arange(4, dtype='float32'), chunk_size=2)
    delete_one_chunk(store_path)

    assert store_has_missing_chunks(store_path) is True


def test_non_finite_zero_for_finite(tmp_path: Path) -> None:
    store_path = tmp_path / 'store.zarr'
    write_store(store_path, np.arange(4, dtype='float32'), chunk_size=2)

    assert store_non_finite_count(store_path) == 0


def test_non_finite_detects_nan(tmp_path: Path) -> None:
    store_path = tmp_path / 'store.zarr'
    data = np.arange(4, dtype='float32')
    data[1] = np.nan
    write_store(store_path, data, chunk_size=2)

    assert store_non_finite_count(store_path) == 1


def build_dummy_kind_tree(chunk_dir, kind, content_by_relpath):
    for relpath, content in content_by_relpath.items():
        store_dir = chunk_dir / kind / relpath
        store_dir.mkdir(parents=True)
        (store_dir / 'data.bin').write_bytes(content)


def test_byte_identical_pass(tmp_path: Path) -> None:
    kind = 'xz'
    relpaths = zarr_relpaths()[kind]
    content_by_relpath = {relpath: b'same content' for relpath in relpaths}

    to_archive_chunk_dir = tmp_path / 'to_archive'
    from_archive_chunk_dir = tmp_path / 'from_archive'
    build_dummy_kind_tree(to_archive_chunk_dir, kind, content_by_relpath)
    build_dummy_kind_tree(from_archive_chunk_dir, kind, content_by_relpath)

    mismatches = check_byte_identical(to_archive_chunk_dir, from_archive_chunk_dir, [kind], Local_backend())

    assert mismatches == []


def test_byte_identical_mismatch(tmp_path: Path) -> None:
    kind = 'xz'
    relpaths = zarr_relpaths()[kind]
    content_by_relpath = {relpath: b'same content' for relpath in relpaths}

    to_archive_chunk_dir = tmp_path / 'to_archive'
    from_archive_chunk_dir = tmp_path / 'from_archive'
    build_dummy_kind_tree(to_archive_chunk_dir, kind, content_by_relpath)
    build_dummy_kind_tree(from_archive_chunk_dir, kind, content_by_relpath)

    corrupted_relpath = relpaths[0]
    corrupted_file = from_archive_chunk_dir / kind / corrupted_relpath / 'data.bin'
    corrupted_file.write_bytes(b'different content')

    mismatches = check_byte_identical(to_archive_chunk_dir, from_archive_chunk_dir, [kind], Local_backend())

    assert mismatches == [str(corrupted_file)]

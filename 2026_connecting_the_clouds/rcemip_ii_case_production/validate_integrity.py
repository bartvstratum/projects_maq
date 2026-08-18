import argparse
import filecmp
import time
from pathlib import Path

from definitions import experiments, env
from expected_output import expected_zarr_relpaths
from filesystem_backend import Local_backend


def check_byte_identical(to_archive_chunk_dir, from_archive_chunk_dir, kinds, backend):
    expected = expected_zarr_relpaths()
    mismatches = []

    for kind in kinds:
        t0 = time.time()
        n_files = 0

        for relpath in expected[kind]:
            to_archive_path = to_archive_chunk_dir / kind / relpath
            from_archive_path = from_archive_chunk_dir / kind / relpath

            for entry in backend.list_tree(to_archive_path):
                f1 = to_archive_path / entry.relpath
                f2 = from_archive_path / entry.relpath
                n_files += 1
                if not filecmp.cmp(f1, f2, shallow=False):
                    mismatches.append(str(f2))

        print(f'- Byte-compared {kind}: {n_files} files, elapsed = {time.time() - t0:.2f} s')

    return mismatches


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', required=True, help='Experiment name')
    parser.add_argument('--start_time', type=int, required=True)
    parser.add_argument('--cross_xz', action='store_true', default=False)
    parser.add_argument('--cross_xy', action='store_true', default=False)
    parser.add_argument('--cross_xy_c', action='store_true', default=False)
    parser.add_argument('--dump_c', action='store_true', default=False)
    parser.add_argument('--convert_all', action='store_true', default=False)
    args = parser.parse_args()

    if args.convert_all:
        args.cross_xz = True
        args.cross_xy = True
        args.cross_xy_c = True
        args.dump_c = True

    print('Validating integrity...')

    exp = experiments[args.exp]
    work_dir = Path(env['work_dir']) / exp['name']

    chunk_idx = args.start_time // exp['time_chunk']
    chunk_name = f'chunk_{chunk_idx:03d}'

    to_archive_chunk_dir = work_dir / 'to_archive' / chunk_name
    from_archive_chunk_dir = work_dir / 'from_archive' / chunk_name

    kinds = []
    if args.cross_xy_c:
        kinds.append('xy_c')
    if args.cross_xy:
        kinds.append('xy')
    if args.cross_xz:
        kinds.append('xz')
    if args.dump_c:
        kinds.append('3d_c')

    backend = Local_backend()
    mismatches = check_byte_identical(to_archive_chunk_dir, from_archive_chunk_dir, kinds, backend)

    if mismatches:
        print(f'Byte-identical check: FAILED, {len(mismatches)} file(s) differ: {mismatches}...')
        raise ValueError(f'{len(mismatches)} file(s) differ between to_archive and from_archive: {mismatches}')

    print('Byte-identical check: PASSED...')
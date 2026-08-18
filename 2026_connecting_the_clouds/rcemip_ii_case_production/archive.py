import argparse
import time
from pathlib import Path

from definitions import experiments, env
from expected_output import expected_zarr_relpaths


def archive_chunk(to_archive_chunk_dir, archive_chunk_dir, from_archive_chunk_dir, kinds, backend):
    expected = expected_zarr_relpaths()

    for kind in kinds:
        t0 = time.time()

        for relpath in expected[kind]:
            to_archive_path = to_archive_chunk_dir / kind / relpath
            archive_path = archive_chunk_dir / kind / relpath
            from_archive_path = from_archive_chunk_dir / kind / relpath

            backend.copy_tree(to_archive_path, archive_path)
            backend.copy_tree(archive_path, from_archive_path)

        print(f'- Archived {kind}: {len(expected[kind])} stores, elapsed = {time.time() - t0:.2f} s')


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

    print('Archiving...')

    exp = experiments[args.exp]
    work_dir = Path(env['work_dir']) / exp['name']
    archive_dir = Path(env['archive_dir']) / exp['name']

    chunk_idx = args.start_time // exp['time_chunk']
    chunk_name = f'chunk_{chunk_idx:03d}'

    to_archive_chunk_dir = work_dir / 'to_archive' / chunk_name
    archive_chunk_dir = archive_dir / chunk_name
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

    backend = env['backend']()
    archive_chunk(to_archive_chunk_dir, archive_chunk_dir, from_archive_chunk_dir, kinds, backend)

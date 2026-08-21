import argparse
import time
from pathlib import Path

from definitions import experiments, env
from expected_output import zarr_relpaths, checkpoint_filenames, stats_filename


def archive_chunk(to_archive_chunk_dir, archive_chunk_dir, from_archive_chunk_dir, kinds, backend):
    expected = zarr_relpaths()

    for kind in kinds:
        t0 = time.time()

        for relpath in expected[kind]:
            to_archive_path = to_archive_chunk_dir / kind / relpath
            archive_path = archive_chunk_dir / kind / relpath
            from_archive_path = from_archive_chunk_dir / kind / relpath

            backend.copy_tree(to_archive_path, archive_path)
            backend.copy_tree(archive_path, from_archive_path)

        print(f'- Archived {kind}: {len(expected[kind])} stores, elapsed = {time.time() - t0:.2f} s')


def archive_raw_files(work_dir, archive_chunk_dir, from_archive_chunk_dir, subdir, filenames, backend):
    t0 = time.time()

    archive_dir = archive_chunk_dir / subdir
    from_archive_dir = from_archive_chunk_dir / subdir

    for filename in filenames:
        src_path = work_dir / filename
        archive_path = archive_dir / filename
        from_archive_path = from_archive_dir / filename

        backend.copy_file(src_path, archive_path)
        backend.copy_file(archive_path, from_archive_path)

    print(f'- Archived {subdir}: {len(filenames)} files, elapsed = {time.time() - t0:.2f} s')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', required=True, help='Experiment name')
    parser.add_argument('--start_time', type=int, required=True)
    parser.add_argument('--end_time', type=int, required=True)
    parser.add_argument('--iotimeprec', type=int, default=1)
    args = parser.parse_args()

    print('Archiving...')

    exp = experiments[args.exp]
    work_dir = Path(env['work_dir']) / exp['name']
    archive_base = env['archive_dir']
    archive_dir = Path(archive_base + exp['name'] if archive_base.endswith(':') else archive_base + '/' + exp['name'])

    chunk_idx = args.start_time // exp['time_chunk']
    chunk_name = f'chunk_{chunk_idx:03d}'

    to_archive_chunk_dir = work_dir / 'to_archive' / chunk_name
    archive_chunk_dir = archive_dir / chunk_name
    from_archive_chunk_dir = work_dir / 'from_archive' / chunk_name

    kinds = []
    if args.start_time >= exp['start_xy_c']:
        kinds.append('xy_c')
    if args.start_time >= exp['start_xy']:
        kinds.append('xy')
    if args.start_time >= exp['start_xz']:
        kinds.append('xz')
    if args.start_time >= exp['start_dump_c']:
        kinds.append('3d_c')

    backend = env['backend']()
    archive_chunk(to_archive_chunk_dir, archive_chunk_dir, from_archive_chunk_dir, kinds, backend)

    stats_file_time = args.start_time // 10**args.iotimeprec
    archive_raw_files(
        work_dir, archive_chunk_dir, from_archive_chunk_dir,
        'stats', [stats_filename('rcemip_ii', stats_file_time)], backend)

    if args.end_time % exp['restart_archive'] == 0:
        file_time = args.end_time // 10**args.iotimeprec
        filenames = checkpoint_filenames(file_time)
        archive_raw_files(
            work_dir, archive_chunk_dir, from_archive_chunk_dir,
            'checkpoint', filenames, backend)

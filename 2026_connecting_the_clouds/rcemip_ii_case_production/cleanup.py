import argparse
import re
import shutil
import time
from pathlib import Path

from definitions import experiments, env
from expected_output import vars_dump_c, restart_vars, stats_filename


cross_pattern = re.compile(r'[^.]+\.(xy|xy_c|xz|yz)\.\d{3}(\.\d{5})?\.(?P<time>\d{7,})')
dump_pattern = re.compile(r'(' + '|'.join(vars_dump_c) + r')_c\.(?P<time>\d{7,})')
restart_pattern = re.compile(r'(' + '|'.join(restart_vars) + r')\.(?P<time>\d{7,})')


def find_files(work_dir, pattern, min_file_time, max_file_time):
    filenames = []

    for path in sorted(work_dir.iterdir()):
        match = pattern.fullmatch(path.name)
        if match is None:
            continue

        file_time = int(match.group('time'))
        if min_file_time <= file_time <= max_file_time:
            filenames.append(path.name)

    return filenames


def remove_chunk_dir(work_dir, subdir, chunk_name):
    t0 = time.time()

    chunk_dir = work_dir / subdir / chunk_name
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir)

    print(f'- Removed {subdir}/{chunk_name}, elapsed = {time.time() - t0:.2f} s')


def remove_files(work_dir, filenames, label):
    t0 = time.time()

    for filename in filenames:
        (work_dir / filename).unlink()

    print(f'- Removed {label}: {len(filenames)} files, elapsed = {time.time() - t0:.2f} s')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', required=True, help='Experiment name')
    parser.add_argument('--start_time', type=int, required=True)
    parser.add_argument('--end_time', type=int, required=True)
    parser.add_argument('--sample_time', type=int, default=3600)
    args = parser.parse_args()

    print('Cleaning up...')

    exp = experiments[args.exp]
    work_dir = Path(env['work_dir']) / exp['name']

    chunk_idx = args.start_time // exp['time_chunk']
    chunk_name = f'chunk_{chunk_idx:03d}'

    remove_chunk_dir(work_dir, 'to_archive', chunk_name)
    remove_chunk_dir(work_dir, 'from_archive', chunk_name)

    first_time = args.start_time if args.start_time == 0 else args.start_time + args.sample_time
    first_file_time = first_time // 10**exp['iotimeprec']
    last_file_time = args.end_time // 10**exp['iotimeprec']

    cross_files = find_files(work_dir, cross_pattern, first_file_time, last_file_time)
    remove_files(work_dir, cross_files, 'cross')

    dump_files = find_files(work_dir, dump_pattern, first_file_time, last_file_time)
    remove_files(work_dir, dump_files, 'dump')

    stats_file_time = args.start_time // 10**exp['iotimeprec']
    remove_files(work_dir, [stats_filename('rcemip_ii', stats_file_time)], 'stats')

    if args.end_time % exp['restart_archive'] == 0 or args.end_time == exp['end_time']:
        restart_files = find_files(work_dir, restart_pattern, 0, last_file_time - 1)
        remove_files(work_dir, restart_files, 'checkpoint')

import argparse
import os
import shutil
import time

import dask
import dask.array as da
import numpy as np
import xarray as xr
from dask.distributed import Client, LocalCluster
from zarr.codecs import BloscCodec

from definitions import experiments, env
from expected_output import vars_xy, vars_xz, vars_dump_c


def bin_path(work_dir, var, kind, locstr, file_time, z=None):
    if z is None:
        return os.path.join(work_dir, f'{var}.{kind}.{locstr}.{file_time:07d}')
    return os.path.join(work_dir, f'{var}.{kind}.{locstr}.{z:05d}.{file_time:07d}')


def dump_c_path(work_dir, var, file_time):
    return os.path.join(work_dir, f'{var}_c.{file_time:07d}')


def stats_nc_path(work_dir, case_name, file_time):
    return os.path.join(work_dir, f'{case_name}.default.{file_time:07d}.nc')


def stage_stats(work_dir, chunk_dir, case_name, start_time, iotimeprec):
    file_time = start_time // 10**iotimeprec
    src = stats_nc_path(work_dir, case_name, file_time)
    os.makedirs(chunk_dir, exist_ok=True)
    shutil.copy2(src, os.path.join(chunk_dir, os.path.basename(src)))
    return os.path.basename(src)


def read_file(path, jtot_c, itot_c):
    return np.fromfile(path, dtype=float_type).reshape(jtot_c, itot_c)


def read_file_3d(path, ktot, jtot_c, itot_c):
    return np.fromfile(path, dtype=float_type).reshape(ktot, jtot_c, itot_c)


def read_grid(work_dir, itot, jtot, ktot):

    data = np.fromfile(os.path.join(work_dir, 'grid.0000000'), dtype=float_type)
    sizes = (itot, itot, jtot, jtot, ktot, ktot)
    names = ('x', 'xh', 'y', 'yh', 'z', 'zh')
    grid = {}
    i = 0
    for name, size in zip(names, sizes):
        grid[name] = data[i:i+size]
        i += size
    return grid


def chunk_info_str(shape, chunks):
    chunksize = da.zeros(shape, chunks=chunks, dtype=float_type).chunksize
    chunk_bytes = np.prod(chunksize) * np.dtype(float_type).itemsize
    return f'chunks={chunksize}, chunk_size={chunk_bytes/1e6:.2f} MB'


def convert_target(paths, times, dim1, coord1, dim2, coord2, n1, n2, chunks, out_path):

    time_chunk, chunk1, chunk2 = chunks

    delayed_reads = [dask.delayed(read_file)(p, n1, n2) for p in paths]
    file_chunks = [da.from_delayed(d, shape=(n1, n2), dtype=float_type) for d in delayed_reads]
    data = da.stack(file_chunks, axis=0).rechunk({0: time_chunk, 1: chunk1, 2: chunk2})

    name = os.path.splitext(os.path.basename(out_path))[0]

    ds = xr.Dataset(
            {name: (('time', dim1, dim2), data)},
            coords={'time': times, dim1: coord1, dim2: coord2})

    ds.to_zarr(out_path, mode='w', consolidated=False, encoding={name: {'compressors': [compressor]}})


def convert_cross(
        work_dir, chunk_dir, kind, vars_xy, grid, file_times, times,
        itot_t, jtot_t, ratio_x, ratio_y, chunks):

    out_dir = os.path.join(chunk_dir, kind)
    os.makedirs(out_dir, exist_ok=True)

    info = chunk_info_str((len(times), jtot_t, itot_t), chunks)

    for var, (locstr, z_indices) in vars_xy.items():
        x_coord = grid['xh' if locstr[0] == '1' else 'x'][::ratio_x]
        y_coord = grid['yh' if locstr[1] == '1' else 'y'][::ratio_y]

        if z_indices is None:
            paths = [bin_path(work_dir, var, kind, locstr, ft) for ft in file_times]
            out_path = os.path.join(out_dir, f'{var}.zarr')
            convert_target(paths, times, 'y', y_coord, 'x', x_coord, jtot_t, itot_t, chunks, out_path)
        else:
            for z in z_indices:
                paths = [bin_path(work_dir, var, kind, locstr, ft, z) for ft in file_times]
                out_path = os.path.join(out_dir, f'{var}_{z}.zarr')
                convert_target(paths, times, 'y', y_coord, 'x', x_coord, jtot_t, itot_t, chunks, out_path)

    return info


def convert_cross_xz(work_dir, chunk_dir, vars_xz, grid, file_times, times, itot, ktot, chunks):

    out_dir = os.path.join(chunk_dir, 'xz')
    os.makedirs(out_dir, exist_ok=True)

    info = chunk_info_str((len(times), ktot, itot), chunks)

    for var, locstr in vars_xz.items():
        x_coord = grid['xh' if locstr[0] == '1' else 'x']
        z_coord = grid['zh' if locstr[2] == '1' else 'z']

        paths = [bin_path(work_dir, f'{var}_ymean', 'xz', locstr, ft) for ft in file_times]
        out_path = os.path.join(out_dir, f'{var}_ymean.zarr')
        convert_target(paths, times, 'z', z_coord, 'x', x_coord, ktot, itot, chunks, out_path)

    return info


def convert_dump_c(work_dir, chunk_dir, vars_dump_c, grid, file_times, times, itot_c, jtot_c, ktot, ratio_x, ratio_y, chunks):

    out_dir = os.path.join(chunk_dir, '3d_c')
    os.makedirs(out_dir, exist_ok=True)

    time_chunk, chunk_z, chunk_y, chunk_x = chunks

    info = chunk_info_str((len(times), ktot, jtot_c, itot_c), chunks)

    for var, locstr in vars_dump_c.items():
        x_coord = grid['xh' if locstr[0] == '1' else 'x'][::ratio_x]
        y_coord = grid['yh' if locstr[1] == '1' else 'y'][::ratio_y]
        z_coord = grid['zh' if locstr[2] == '1' else 'z']

        paths = [dump_c_path(work_dir, var, ft) for ft in file_times]
        out_path = os.path.join(out_dir, f'{var}.zarr')

        delayed_reads = [dask.delayed(read_file_3d)(p, ktot, jtot_c, itot_c) for p in paths]
        file_chunks = [da.from_delayed(d, shape=(ktot, jtot_c, itot_c), dtype=float_type) for d in delayed_reads]
        data = da.stack(file_chunks, axis=0).rechunk({0: time_chunk, 1: chunk_z, 2: chunk_y, 3: chunk_x})

        ds = xr.Dataset(
                {var: (('time', 'z', 'y', 'x'), data)},
                coords={'time': times, 'z': z_coord, 'y': y_coord, 'x': x_coord})

        ds.to_zarr(out_path, mode='w', consolidated=False, encoding={var: {'compressors': [compressor]}})

    return info


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', required=True, help='Experiment name')
    parser.add_argument('--start_time', type=int, required=True)
    parser.add_argument('--end_time', type=int, required=True)
    parser.add_argument('--cross_xz', action='store_true', default=False)
    parser.add_argument('--cross_xy', action='store_true', default=False)
    parser.add_argument('--cross_xy_c', action='store_true', default=False)
    parser.add_argument('--dump_c', action='store_true', default=False)
    parser.add_argument('--convert_all', action='store_true', default=False)
    parser.add_argument('--iotimeprec', type=int, default=1)
    parser.add_argument('--sample_time', type=int, default=3600)
    args = parser.parse_args()

    if args.convert_all:
        args.cross_xz = True
        args.cross_xy = True
        args.cross_xy_c = True
        args.dump_c = True

    float_type = np.float32

    n_workers = 6
    threads_per_worker = 1

    compressor = BloscCodec(cname='lz4', clevel=1, shuffle='shuffle')

    first_time = args.start_time if args.start_time == 0 else args.start_time + args.sample_time
    times = np.arange(first_time, args.end_time + 1, args.sample_time)
    file_times = times // 10**args.iotimeprec

    exp = experiments[args.exp]
    work_dir = os.path.abspath(os.path.join(env['work_dir'], exp['name']))

    itot = exp['itot']
    jtot = exp['jtot']
    ktot = 128  # Jikes!

    itot_c = itot // exp['coarse_ratio_x']
    jtot_c = jtot // exp['coarse_ratio_y']

    print(f'Post-processing...')

    grid = read_grid(work_dir, itot, jtot, ktot)
    ratio_x = exp['coarse_ratio_x']
    ratio_y = exp['coarse_ratio_y']

    cluster = LocalCluster(n_workers=n_workers, threads_per_worker=threads_per_worker)
    client = Client(cluster)

    chunk_idx = args.start_time // exp['time_chunk']
    chunk_dir = os.path.join(work_dir, 'to_archive', f'chunk_{chunk_idx:03d}')

    t0 = time.time()
    stats_name = stage_stats(work_dir, chunk_dir, 'rcemip_ii', args.start_time, args.iotimeprec)
    print(f'- Staging {stats_name}, elapsed = {time.time() - t0:.2f} s')

    if args.cross_xy_c:
        t0 = time.time()
        info = convert_cross(
            work_dir, chunk_dir, 'xy_c', vars_xy, grid, file_times, times,
            itot_c, jtot_c, ratio_x, ratio_y, exp['chunks_xy_c'])
        print(f'- Converting xy_c: {info}, elapsed = {time.time() - t0:.2f} s')

    if args.cross_xy:
        t0 = time.time()
        info = convert_cross(
            work_dir, chunk_dir, 'xy', vars_xy, grid, file_times, times,
            itot, jtot, 1, 1, exp['chunks_xy'])
        print(f'- Converting xy: {info}, elapsed = {time.time() - t0:.2f} s')

    if args.cross_xz:
        t0 = time.time()
        info = convert_cross_xz(work_dir, chunk_dir, vars_xz, grid, file_times, times, itot, ktot, exp['chunks_xz'])
        print(f'- Converting xz: {info}, elapsed = {time.time() - t0:.2f} s')

    if args.dump_c:
        t0 = time.time()
        info = convert_dump_c(
            work_dir, chunk_dir, vars_dump_c, grid, file_times, times,
            itot_c, jtot_c, ktot, ratio_x, ratio_y, exp['chunks_dump_c'])
        print(f'- Converting 3d_c: {info}, elapsed = {time.time() - t0:.2f} s')

    client.close()

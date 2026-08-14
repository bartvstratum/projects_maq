import argparse
import os

import dask
import dask.array as da
import numpy as np
import xarray as xr
from dask.distributed import Client, LocalCluster
from zarr.codecs import BloscCodec

from definitions import experiments, env


def bin_path(work_dir, var, locstr, file_time, z=None):
    if z is None:
        return os.path.join(work_dir, f'{var}.xy_c.{locstr}.{file_time:07d}')
    return os.path.join(work_dir, f'{var}.xy_c.{locstr}.{z:05d}.{file_time:07d}')


def read_file(path, jtot_c, itot_c):
    return np.fromfile(path, dtype=float_type).reshape(jtot_c, itot_c)


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


def convert_target(paths, times, x_coord, y_coord, jtot_c, itot_c, chunks, out_path):
    time_chunk, y_chunk, x_chunk = chunks

    delayed_reads = [dask.delayed(read_file)(p, jtot_c, itot_c) for p in paths]
    file_chunks = [da.from_delayed(d, shape=(jtot_c, itot_c), dtype=float_type) for d in delayed_reads]
    data = da.stack(file_chunks, axis=0).rechunk({0: time_chunk, 1: y_chunk, 2: x_chunk})

    name = os.path.splitext(os.path.basename(out_path))[0]
    ds = xr.Dataset(
            {name: (('time', 'y', 'x'), data)},
            coords={'time': times, 'y': y_coord, 'x': x_coord})

    ds.to_zarr(out_path, mode='w', consolidated=False, encoding={name: {'compressors': [compressor]}})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--exp', required=True, help='Experiment name')
    parser.add_argument('--start_time', type=int, required=True)
    parser.add_argument('--end_time', type=int, required=True)
    parser.add_argument('--cross_xz', action='store_true', default=False)
    parser.add_argument('--cross_xy', action='store_true', default=False)
    parser.add_argument('--cross_xy_c', action='store_true', default=False)
    parser.add_argument('--dump_c', action='store_true', default=False)
    parser.add_argument('--iotimeprec', type=int, default=1)
    parser.add_argument('--sample_time', type=int, default=3600)
    args = parser.parse_args()

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

    print(f'Post-processing exp={args.exp}: itot={itot}, jtot={jtot} | itot_c={itot_c}, jtot_c={jtot_c}')

    grid = read_grid(work_dir, itot, jtot, ktot)
    ratio_x = exp['coarse_ratio_x']
    ratio_y = exp['coarse_ratio_y']

    vars_xy_coarse = dict(
        rrsg_bot          = ('000', None),
        thl_fluxbot       = ('000', None),
        qt_fluxbot        = ('000', None),
        lw_flux_dn        = ('001', (0, 128)),
        lw_flux_up        = ('001', (0, 128)),
        sw_flux_dn        = ('001', (0, 128)),
        sw_flux_up        = ('001', (0, 128)),
        sw_flux_dn_clear  = ('001', (0, 128)),
        sw_flux_up_clear  = ('001', (0, 128)),
        lw_flux_dn_clear  = ('001', (0, 128)),
        lw_flux_up_clear  = ('001', (0, 128)),
        qt_path           = ('000', None),
        qsat_path         = ('000', None),
        qlqi_path         = ('000', None),
        qi_path           = ('000', None),
        t2m               = ('000', None),
        u10m              = ('100', None),
        v10m              = ('010', None),
        thl               = ('000', (0,)),
        u                 = ('100', (0,)),
        v                 = ('010', (0,)),
        w500hpa           = ('000', None),
    )

    cluster = LocalCluster(n_workers=n_workers, threads_per_worker=threads_per_worker)
    client = Client(cluster)

    if args.cross_xy_c:
        chunk_dir = os.path.join(work_dir, f'{args.start_time:07d}')
        os.makedirs(chunk_dir, exist_ok=True)
        chunks = exp['chunks_xy_c']

        for var, (locstr, z_indices) in vars_xy_coarse.items():
            x_coord = grid['xh' if locstr[0] == '1' else 'x'][::ratio_x]
            y_coord = grid['yh' if locstr[1] == '1' else 'y'][::ratio_y]

            if z_indices is None:
                paths = [bin_path(work_dir, var, locstr, ft) for ft in file_times]
                out_path = os.path.join(chunk_dir, f'{var}.zarr')
                convert_target(paths, times, x_coord, y_coord, jtot_c, itot_c, chunks, out_path)
            else:
                for z in z_indices:
                    paths = [bin_path(work_dir, var, locstr, ft, z) for ft in file_times]
                    out_path = os.path.join(chunk_dir, f'{var}_{z}.zarr')
                    convert_target(paths, times, x_coord, y_coord, jtot_c, itot_c, chunks, out_path)

    client.close()
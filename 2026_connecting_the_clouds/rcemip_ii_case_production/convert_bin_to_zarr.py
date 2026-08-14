import argparse
import glob
import os

import dask
import dask.array as da
import numpy as np
import xarray as xr
from dask.distributed import Client, LocalCluster
from zarr.codecs import BloscCodec

from definitions import experiments, env


def bin_path_2d(work_dir, var, file_time):
    return os.path.join(work_dir, f'{var}.xy_c.000.{file_time:07d}')


def bin_path_z(work_dir, var, locstr, z, file_time):
    return os.path.join(work_dir, f'{var}.xy_c.{locstr}.{z:05d}.{file_time:07d}')


def find_locstr(work_dir, var, z, file_time):
    pattern = os.path.join(work_dir, f'{var}.xy_c.???.{z:05d}.{file_time:07d}')
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(pattern)
    return os.path.basename(matches[0]).split('.')[2]


def read_file(path, jtot_c, itot_c):
    return np.fromfile(path, dtype=float_type).reshape(jtot_c, itot_c)


def convert_target(paths, times, jtot_c, itot_c, chunks, out_path):
    time_chunk, y_chunk, x_chunk = chunks

    delayed_reads = [dask.delayed(read_file)(p, jtot_c, itot_c) for p in paths]
    file_chunks = [da.from_delayed(d, shape=(jtot_c, itot_c), dtype=float_type) for d in delayed_reads]
    data = da.stack(file_chunks, axis=0).rechunk({0: time_chunk, 1: y_chunk, 2: x_chunk})

    name = os.path.splitext(os.path.basename(out_path))[0]
    ds = xr.Dataset(
            {name: (('time', 'y', 'x'), data)},
            coords={'time': times})

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

    vars_xy_coarse = dict(
        rrsg_bot          = None,
        thl_fluxbot       = None,
        qt_fluxbot        = None,
        lw_flux_dn        = (0, 128),
        lw_flux_up        = (0, 128),
        sw_flux_dn        = (0, 128),
        sw_flux_up        = (0, 128),
        sw_flux_dn_clear  = (0, 128),
        sw_flux_up_clear  = (0, 128),
        lw_flux_dn_clear  = (0, 128),
        lw_flux_up_clear  = (0, 128),
        qt_path           = None,
        qsat_path         = None,
        qlqi_path         = None,
        qi_path           = None,
        t2m               = None,
        u10m              = None,
        v10m              = None,
        thl               = (0),
        u                 = (0),
        v                 = (0),
        w500hpa           = None,
    )

    cluster = LocalCluster(n_workers=n_workers, threads_per_worker=threads_per_worker)
    client = Client(cluster)

    if args.cross_xy_c:
        chunk_dir = os.path.join(work_dir, f'{args.start_time:07d}')
        os.makedirs(chunk_dir, exist_ok=True)
        chunks = exp['chunks_xy_c']

        for var, z_indices in vars_xy_coarse.items():
            if z_indices is None:
                paths = [bin_path_2d(work_dir, var, ft) for ft in file_times]
                out_path = os.path.join(chunk_dir, f'{var}.zarr')
                convert_target(paths, times, jtot_c, itot_c, chunks, out_path)
            else:
                zs = (z_indices,) if isinstance(z_indices, int) else z_indices
                locstr = find_locstr(work_dir, var, zs[0], file_times[0])

                for z in zs:
                    paths = [bin_path_z(work_dir, var, locstr, z, ft) for ft in file_times]
                    out_path = os.path.join(chunk_dir, f'{var}_{z}.zarr')
                    convert_target(paths, times, jtot_c, itot_c, chunks, out_path)

    client.close()

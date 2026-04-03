#
#  MicroHH
#  Copyright (c) 2011-2024 Chiel van Heerwaarden
#  Copyright (c) 2011-2024 Thijs Heus
#  Copyright (c) 2014-2024 Bart van Stratum
#
#  This file is part of MicroHH
#
#  MicroHH is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MicroHH is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MicroHH.  If not, see <http://www.gnu.org/licenses/>.
#

import subprocess
import os

import numpy as np

# `pip install ls2d`
import ls2d

# `mock_walker.py` help functions.
from rcemip_ii import rcemip_ii_input
import global_settings as env


"""
Global settings.
"""
float_type = np.float32

sw_cos_sst = False  # False for RCEMIP-I, True for RCEMIP-II
mean_sst = 300
d_sst = 2.5
ps = 101480
endtime = 900

#coef_sw='rrtmgp-gas-sw-g049-cf2.nc'
#coef_lw='rrtmgp-gas-lw-g056-cf2.nc'

coef_sw = 'rrtmgp-gas-sw-g112.nc'
coef_lw = 'rrtmgp-gas-lw-g128.nc'

create_slurm_script = True
wc_time = '06:00:00'

"""
Scaling uses a fixed time step.
At cold start, dynamics are undeveloped so the dynamic dt is too large,
causing statistics/IO/radiation to be called unrealistically often.
These time steps were estimated from longer simulations on the ECMWF HPC.
"""
dt_200 = 4.4
dt_400 = 5.1
dt_800 = 3.5    # Yikes; limited by diffusion because of the pancake grid cells.


def run_scaling(exp_settings, rotated_domain=False, lfs_c=1, lfs_s='1M'):
    """
    Run weak scaling set for all configs.
    """
    name = exp_settings['name']
    print(f'====== Running {name} ======')

    if exp_settings['ktot'] == 128:
        # Custom 128h layer grid.
        z = np.array([0, 3_000, 15_000, 100_000])
        f = np.array([1.05, 1.00, 1.055])
        grid = ls2d.grid.Grid_stretched_manual(128, 40, z, f)
        z = grid.z
        zsize = grid.zsize

    elif exp_settings['ktot'] == 144:
        # Official RCEMIP LES grid.
        z = np.loadtxt('rcemip_les_grid.txt')
        z = z[:-2]   # From 146 to 144 levels for domain decomposition.
        zsize = 32250

    else:
        raise Exception('Invalid vertical grid.')

    for nn_x, nn_y in exp_settings['configs']:

        itot = exp_settings['itot_b'] * nn_x
        jtot = exp_settings['jtot_b'] * nn_y

        npx = exp_settings['npx_b'] * nn_x
        npy = exp_settings['npy_b'] * nn_y

        xsize = itot * exp_settings['dxy']
        ysize = jtot * exp_settings['dxy']

        dt_max = exp_settings['dt']

        case_name = f'{name}_{nn_x}x{nn_y}'
        case_path = f'{env.work_dir}/{name}/{nn_x}x{nn_y}'

        if os.path.exists(case_path):
            print('Case already exists! Skipping...')
        else:
            os.makedirs(case_path)
            copy_out_to = env.work_dir

            slurm_script = rcemip_ii_input(
                    case_name,
                    xsize,
                    ysize,
                    itot,
                    jtot,
                    npx,
                    npy,
                    z,
                    zsize,
                    endtime,
                    sw_cos_sst,
                    mean_sst,
                    d_sst,
                    ps,
                    rotated_domain,
                    coef_sw,
                    coef_lw,
                    wc_time,
                    case_path,
                    env.gpt_path,
                    env.microhh_path,
                    env.microhh_bin,
                    create_slurm_script,
                    env.project,
                    env.partition,
                    copy_out_to,
                    lfs_c,
                    lfs_s,
                    dt_max,
                    float_type)

            subprocess.run(['sbatch', slurm_script], check=True)


def run_io_benchmark():
    """
    MPI-IO LFS striping settings.
    """
    stripe_count=None
    stripe_size=None
    run_scaling(dict(name=f'200_128_{stripe_count}_{stripe_size}', itot_b=1920, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, configs=[(2,2)]), lfs_c=stripe_count, lfs_s=stripe_size)

    for stripe_count in [1, 2, 4, 8, 16, 32]:
        for stripe_size in ['1M', '2M', '4M']:
            run_scaling(dict(name=f'200_128_{stripe_count}_{stripe_size}', itot_b=1920, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, configs=[(2,2)]), lfs_c=stripe_count, lfs_s=stripe_size)


def run_200m_scaling():
    """
    200 m, 128 levels.
    """
    settings = (
        dict(name='200_128_16x1', itot_b=1920, jtot_b=2048, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(1,1), (2,1), (4,1), (8,1), (16,1)]),
        dict(name='200_128_16x2', itot_b=1920, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(1,1), (1,2), (2,2), (4,2), (8,2), (16,2)]),
        dict(name='200_128_16x4', itot_b=1920, jtot_b= 512, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(1,1), (1,2), (1,4), (2,4), (4,4), (8,4), (16,4)]),
        dict(name='200_128_16x8', itot_b=1920, jtot_b= 256, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(1,1), (1,2), (1,4), (1,8), (2,8), (4,8), (8,8), (16,8)]),
        )

    rotated = False
    for setting in settings:
        run_scaling(setting, rotated, lfs_c=16, lfs_s='2M')


def run_400m_scaling():
    """
    400 m, 128 vertical levels.
    """
    settings = (
        dict(name='400_128_4x1',  itot_b=3840, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=390.625, dt=dt_400, configs=[(1,1), (2,1), (4,1)]),
        dict(name='400_128_8x1',  itot_b=1920, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=390.625, dt=dt_400, configs=[(1,1), (2,1), (4,1), (8,1)]),
        dict(name='400_128_16x1', itot_b=960,  jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=390.625, dt=dt_400, configs=[(1,1), (2,1), (4,1), (8,1), (16,1)]),
        dict(name='400_128_16x2', itot_b=960,  jtot_b= 512, ktot=128, npx_b=8, npy_b=16, dxy=390.625, dt=dt_400, configs=[(1,1), (1,2), (2,2), (4,2), (8,2), (16,2)]),
        dict(name='400_128_16x4', itot_b=960,  jtot_b= 256, ktot=128, npx_b=8, npy_b=16, dxy=390.625, dt=dt_400, configs=[(1,1), (1,2), (1,4), (2,4), (4,4), (8,4), (16,4)])
    )

    rotated = False
    for setting in settings:
        run_scaling(setting, rotated, lfs_c=16, lfs_s='2M')


def run_800m_scaling():
    """
    800 m, 128 vertical levels.
    """
    settings = (
        dict(name='800_128_4x1',  itot_b=1920, jtot_b=512, ktot=128, npx_b=8, npy_b=16, dxy=781.25, dt=dt_800, configs=[(1,1), (2,1), (4,1)]),
        dict(name='800_128_8x1',  itot_b=960,  jtot_b=512, ktot=128, npx_b=8, npy_b=16, dxy=781.25, dt=dt_800, configs=[(1,1), (2,1), (4,1), (8,1)]),
        dict(name='800_128_16x1', itot_b=480,  jtot_b=512, ktot=128, npx_b=8, npy_b=16, dxy=781.25, dt=dt_800, configs=[(1,1), (2,1), (4,1), (8,1), (16,1)]),
    )

    rotated = False
    for setting in settings:
        run_scaling(setting, rotated, lfs_c=16, lfs_s='2M')


def run_strong_scaling():
    """
    Strong scaling for all resolutions.
    """

    settings = (
        dict(name='200_128_16x1', itot_b=1920, jtot_b=2048, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(16,1)]),
        dict(name='200_128_16x2', itot_b=1920, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(16,2)]),
        dict(name='200_128_16x4', itot_b=1920, jtot_b= 512, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(16,4)]),
        dict(name='200_128_16x8', itot_b=1920, jtot_b= 256, ktot=128, npx_b=8, npy_b=16, dxy=195.3125, dt=dt_200, configs=[(16,8)]),
        dict(name='400_128_8x1',  itot_b=1920, jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=390.625,  dt=dt_400, configs=[(8, 1)]),
        dict(name='400_128_16x1', itot_b=960,  jtot_b=1024, ktot=128, npx_b=8, npy_b=16, dxy=390.625,  dt=dt_400, configs=[(16,1)]),
        dict(name='400_128_16x2', itot_b=960,  jtot_b= 512, ktot=128, npx_b=8, npy_b=16, dxy=390.625,  dt=dt_400, configs=[(16,2)]),
        dict(name='400_128_16x4', itot_b=960,  jtot_b= 256, ktot=128, npx_b=8, npy_b=16, dxy=390.625,  dt=dt_400, configs=[(16,4)]),
        dict(name='800_128_4x1',  itot_b=1920, jtot_b=512,  ktot=128, npx_b=8, npy_b=16, dxy=781.25,   dt=dt_800, configs=[(4, 1)]),
        dict(name='800_128_8x1',  itot_b=960,  jtot_b=512,  ktot=128, npx_b=8, npy_b=16, dxy=781.25,   dt=dt_800, configs=[(8, 1)]),
        dict(name='800_128_16x1', itot_b=480,  jtot_b=512,  ktot=128, npx_b=8, npy_b=16, dxy=781.25,   dt=dt_800, configs=[(16,1)]),
        )

    rotated = False
    for setting in settings:
        run_scaling(setting, rotated, lfs_c=16, lfs_s='2M')


if __name__ == '__main__':

    #run_io_benchmark()

    run_200m_scaling()
    run_400m_scaling()
    run_800m_scaling()

    #run_strong_scaling()

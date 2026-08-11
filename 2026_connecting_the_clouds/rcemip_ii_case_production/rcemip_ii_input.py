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

import os
import numpy as np

import ls2d

from rcemip_ii import rcemip_ii_input




"""
Global settings, same for all RCEMIP-II cases.
"""
float_type = np.float32

# G-point sets from Veerman (2024).
coef_sw = 'rrtmgp-gas-sw-g049-cf2.nc'
coef_lw = 'rrtmgp-gas-lw-g056-cf2.nc'

# Lustre striping settings -- tuned for LUMI.

# Vertical grid.
# 128, same as RCEMIP <15 km, more agressive stretching above.
z = np.array([0, 3_000, 15_000, 100_000])
f = np.array([1.05, 1.00, 1.055])
grid = ls2d.grid.Grid_stretched_manual(128, 40, z, f)

"""
Compute environments.
"""
env_eddy = dict(
    project = None,
    partition = None,
    lfs_c = None,
    lfs_s = None,
    gpt_path = '/home/bart/meteo/models/coefficients_veerman/',
    microhh_path = '/home/bart/meteo/models/microhh/',
    microhh_bin = '/home/bart/meteo/models/microhh/build_sp_gpu/microhh',
    work_dir = 'test',
)

"""
Experiment specific settings.
"""
exp_rcemip_1 = dict(
    name = 'rcemip_i'
    mean_sst = 300,
    delta_sst = 2.5,
    sw_cos_sst = False,
    ps = 101480,
    xsize = 240*200,
    ysize = 240*200,
    itot = 240,
    jtot = 240,
    npx = 1,
    npy = 1,
    coarse_ratio_x = 16,
    coarse_ratio_y = 16
    end_time = 2*24*3600,
    )

exp_800m_d2_5 = dict(
    name = 'rce_800_d2.5'
    mean_sst = 300,
    delta_sst = 2.5,
    sw_cos_sst = True,
    ps = 101480,
    xsize = 7680*781.25,
    ysize = 512*781.25,
    itot = 7680,
    jtot = 512,
    npx = 64,
    npy = 16,
    coarse_ratio_x = 4,
    coarse_ratio_y = 4
    end_time = 150*24*3600,
    )


"""
Generate case input.
Only needed once per experiment -- SLURM script does the restarts/archiving/...
"""
exp = exp_rcemip_1
env = env_eddy

work_dir = os.path.join(env['work_dir'], exp['name']),

if not os.path.exists(work_dir):
    os.makedirs(work_dir)

rcemip_ii_input(
        name = exp['name'],
        xsize = exp['xsize'],
        ysize = exp['ysize'],
        itot = exp['itot'],
        jtot = exp['jtot'],
        npx = exp['npx'],
        npy = exp['npy'],
        z = grid.z,
        zsize = grid.zsize,
        endtime = exp['end_time'],
        sw_cos_sst = exp['sw_cos_sst'],
        mean_sst = exp['mean_sst'],
        d_sst = exp['delta_sst'],
        ps = exp['ps'],
        sw_rotated_domain = False,
        coef_sw = coef_sw,
        coef_lw = coef_lw,
        wc_time = None,
        work_dir = work_dir,
        gpt_path = env['gpt_path'],
        microhh_path = env['microhh_path'],
        microhh_bin = env['microhh_bin'],
        create_slurm_script = False,
        account = env['project'],
        partition = env['partition'],
        copy_out_to = None,
        lfc_c = env['lfs_c'],
        lfs_s = env['lfs_s'],
        dt_max = None,
        ratio_x = exp['coarse_ratio_x'],
        ratio_y = exp['coarse_ratio_y'],
        float_type = float_type)
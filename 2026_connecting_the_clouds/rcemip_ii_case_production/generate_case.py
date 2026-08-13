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
import argparse
import numpy as np

import ls2d

from case_setup import rcemip_ii_input
from definitions import experiments, env

"""
Parse command line arguments.
"""
parser = argparse.ArgumentParser()
parser.add_argument('--exp', required=True, help='Experiment name')
args = parser.parse_args()


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
Generate case input.
"""
exp = experiments[args.exp]

work_dir = os.path.join(env['work_dir'], exp['name'])

if not os.path.exists(work_dir):
    os.makedirs(work_dir)

rcemip_ii_input(
        name = exp['name'],
        xsize = exp['xsize'],
        ysize = exp['ysize'],
        itot = exp['itot'],
        jtot = exp['jtot'],
        c_ratio_x = exp['coarse_ratio_x'],
        c_ratio_y = exp['coarse_ratio_y'],
        npx = exp['npx'],
        npy = exp['npy'],
        z = grid.z,
        zsize = grid.zsize,
        sw_cos_sst = exp['sw_cos_sst'],
        mean_sst = exp['mean_sst'],
        d_sst = exp['delta_sst'],
        ps = exp['ps'],
        coef_sw = coef_sw,
        coef_lw = coef_lw,
        work_dir = work_dir,
        gpt_path = env['gpt_path'],
        microhh_path = env['microhh_path'],
        microhh_bin = env['microhh_bin'],
        float_type = float_type)

print(f'Created experiment \"{exp["name"]}\" in {work_dir}')

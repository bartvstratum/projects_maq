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
import matplotlib.pyplot as plt
from datetime import datetime

from numba import jit, prange

class Grid:
    def __init__(self, xsize, ysize, itot, jtot, ktot):

        self.xsize = xsize
        self.ysize = ysize

        self.itot = itot
        self.jtot = jtot
        self.ktot = ktot

        self.dx = xsize / itot
        self.dy = ysize / jtot

        self.x = np.arange(self.dx/2, xsize, self.dx)
        self.xh = np.arange(0, xsize, self.dx)

        self.y = np.arange(self.dy/2, ysize, self.dy)
        self.yh = np.arange(0, ysize, self.dy)


def calc_nn_indices(x_in, x_out):
    """
    Calculate nearest-neighbour indexes.
    """
    return np.array([np.argmin(np.abs(x_in - x)) for x in x_out])


@jit(nopython=True, fastmath=True, nogil=True, parallel=True)
def interp_kernel_3d(fld_out, fld_in, nn_i, nn_j, itot, jtot, ktot):
    """
    Fast parallel NN interpolation kernel.
    """
    for k in prange(ktot):
        for j in prange(jtot):
            for i in prange(itot):
                fld_out[k,j,i] = fld_in[k, nn_j[j], nn_i[i]]


@jit(nopython=True, fastmath=True, nogil=True, parallel=True)
def interp_kernel_2d(fld_out, fld_in, nn_i, nn_j, itot, jtot):
    """
    Fast parallel NN interpolation kernel.
    """
    for j in prange(jtot):
        for i in prange(itot):
            fld_out[j,i] = fld_in[nn_j[j], nn_i[i]]


def interp_nn(fld_in, x_in, y_in, x_out, y_out, float_type):
    """
    Nearest neighbour interpolation.
    """
    ktot = fld_in.shape[0]
    jtot = y_out.size
    itot = x_out.size

    nn_i = calc_nn_indices(x_in, x_out)
    nn_j = calc_nn_indices(y_in, y_out)

    if fld_in.ndim == 2:
        fld_out = np.zeros((jtot, itot), dtype=float_type)
        interp_kernel_2d(fld_out, fld_in, nn_i, nn_j, itot, jtot)

    elif fld_in.ndim == 3:
        fld_out = np.zeros((ktot, jtot, itot), dtype=float_type)
        interp_kernel_3d(fld_out, fld_in, nn_i, nn_j, itot, jtot, ktot)

    return fld_out


def parse_field(variable, grid_in, x_in, y_in, x_out, y_out, time_in, time_out, path_in, path_out, float_type, is_3d=True):

    shape = (grid_in.ktot, grid_in.jtot, grid_in.itot) if is_3d else (grid_in.jtot, grid_in.itot)

    file_in  = f'{path_in}/{variable}.{time_in:07d}'
    file_out = f'{path_out}/{variable}.{time_out:07d}'

    fld_in = np.fromfile(file_in, dtype=float_type).reshape(shape)
    fld_out = interp_nn(fld_in, x_in, y_in, x_out, y_out, float_type)
    fld_out.tofile(file_out)

    #plt.figure()
    #ax=plt.subplot(121)
    #plt.pcolormesh(grid_in.x, grid_in.y, fld_in[2,:,:])
    #plt.colorbar()

    #plt.subplot(122, sharex=ax, sharey=ax)
    #plt.pcolormesh(grid_out.x, grid_out.y, fld_out[2,:,:])
    #plt.colorbar()



"""
Settings.
"""
float_type = np.float32

ktot = 128

# Test.
grid_in  = Grid(25_600, 25_600, 64,  64,  ktot)
grid_out = Grid(25_600, 25_600, 128, 128, ktot)

# Full domain.
#xsize = 30720*200
#ysize = 2048*200
#grid_in = Grid(xsize, ysize, 15360, 1024, ktot)
#grid_out  = Grid(xsize, ysize, 30720, 2048, ktot)

path_in = 'test_400m'
path_out = 'test_200m'

# Time including iotimeprec scaling.
time_in = 4320
time_out = 0

tic = datetime.now()

# Half-level 3D fields in x/y:
parse_field('u', grid_in, grid_in.xh, grid_in.y, grid_out.xh, grid_out.y, time_in, time_out, path_in, path_out, float_type, True)
parse_field('v', grid_in, grid_in.x, grid_in.yh, grid_out.x, grid_out.yh, time_in, time_out, path_in, path_out, float_type, True)

# Full level 3D fields in x/y:
for var in ('w', 'thl', 'qt', 'qr', 'qs', 'qg'):
    parse_field(var, grid_in, grid_in.x, grid_in.y, grid_out.x, grid_out.y, time_in, time_out, path_in, path_out, float_type, True)

# 2D fields. NOTE: dudz and dvdz are also at full levels.
for var in ('dbdz_mo', 'dudz_mo', 'dvdz_mo', 'obuk', 'qt_bot', 'thl_bot'):
    parse_field(var, grid_in, grid_in.x, grid_in.y, grid_out.x, grid_out.y, time_in, time_out, path_in, path_out, float_type, False)

toc = datetime.now()
print(f'Interpolations took {toc-tic}...')
import glob
import argparse

from microhhpy.io import read_ini, save_ini

"""
Parse cmd line arguments.
"""
parser = argparse.ArgumentParser()
parser.add_argument('-wd', required=True, help='Working directory')
parser.add_argument('-start_time', type=int, required=True)
parser.add_argument('-end_time', type=int, required=True)
parser.add_argument('-total_time', type=int, required=True)
args = parser.parse_args()


"""
Settings. What output is saved when?
"""
output_coarse_xy = args.total_time
output_native_xz = args.total_time
output_native_xy = 1*24*3600
output_coarse_3d = 2*24*3600

crosslist_xy = [
        'rrsg_bot', 'thl_fluxbot', 'qt_fluxbot',
        'lw_flux_dn', 'lw_flux_up', 'sw_flux_dn', 'sw_flux_up',
        'sw_flux_dn_clear', 'sw_flux_up_clear', 'lw_flux_dn_clear', 'lw_flux_up_clear',
        'qt_path', 'qsat_path', 'qlqi_path', 'qi_path',
        't2m', 'u10m', 'v10m',
        'thl', 'u', 'v', 'w500hpa']

crosslist_xz = ['thl', 'qt', 'ql', 'qi', 'qr', 'qs', 'qg', 'u', 'w']

dumplist_coarse = [
        'u', 'v', 'w', 'thl', 'qt', 'ql', 'qi', 'qr', 'qs', 'qg',
        'thl_tend', 'qt_tend', 'w_tend', 'thl_tend_lw', 'thl_tend_sw',
        'qrsg_tend_sed', 'qtr_tend_frz',
        'uthl', 'vthl', 'wthl', 'uqt', 'vqt', 'wqt', 'wqr', 'wql', 'wqi', 'uw', 'vw']


"""
Read base .ini file and set values.
"""
ini = read_ini(f'{args.wd}/rcemip_ii.ini.base')

ini['time']['starttime'] = args.start_time
ini['time']['endtime'] = args.end_time
ini['time']['savetime'] = args.end_time-args.start_time

# Determine wheter to trigger cross/dump output:
time_left = args.total_time - args.start_time

save_coarse_xy = time_left <= output_coarse_xy
save_native_xy = time_left <= output_native_xy
save_native_xz = time_left <= output_native_xz
save_coarse_3d = time_left <= output_coarse_3d

if save_coarse_xy or save_native_xy or save_native_xz:
    print('Enabling cross-sections')
    ini['cross']['swcross'] = True

if save_coarse_xy:
    print('Enabling coarse XY cross-sections')
    ini['cross']['crosslist_coarse'] = crosslist_xy
if save_native_xy:
    print('Enabling native XY cross-sections')
    ini['cross']['crosslist'] = crosslist_xy
if save_native_xz:
    print('Enabling native XZ cross-sections')
    ini['cross']['crosslist_ymean'] = crosslist_xz

if save_coarse_3d:
    print('Enabling coarse 3D dumps')
    ini['dump']['swdump'] = True
    ini['dump']['dumplist_coarse'] = dumplist_coarse


"""
Write final .ini file.
"""
save_ini(ini, f'{args.wd}/rcemip_ii.ini')

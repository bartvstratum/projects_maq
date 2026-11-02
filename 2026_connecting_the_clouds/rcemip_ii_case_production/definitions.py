import numpy as np

from filesystem_backend import Local_backend, Rclone_backend

#float_type = np.float64
float_type = np.float32

"""
Compute environments.
Make sure all paths are ABSOLUTE!
"""

#lumi_project = 'project_465003023'   # MicroHH3 development acccess call.
lumi_project = 'project_465003624'   # Extreme-scale access.

compute_env = dict(
    eddy = dict(
        project = None,
        partition = None,
        post_partition = None,
        lfs_c = None,
        lfs_s = None,
        gpt_path = '/home/bart/meteo/models/coefficients_veerman/',
        microhh_path = '/home/bart/meteo/models/microhh/',
        #microhh_bin = '/home/bart/meteo/models/microhh/build_sp_gpu/microhh',
        env_setup = None,
        #microhh_bin = '/home/bart/meteo/models/microhh/build_spdp_cpumpi/microhh',
        microhh_bin = '/home/bart/meteo/models/microhh/build_dp_cpumpi/microhh',
        work_dir = '/home/bart/meteo/projects_maq/2026_connecting_the_clouds/rcemip_ii_case_production/experiments',
        archive_dir = '/home/bart/meteo/projects_maq/2026_connecting_the_clouds/rcemip_ii_case_production/archive',
        backend = Local_backend,
        ),

    ecmwf = dict(
        project = None,
        partition = 'par',
        post_partition = 'par',
        lfs_c = None,
        lfs_s = None,
        gpt_path = '/home/nkbs/meteo/models/coefficients_veerman',
        microhh_path = '/home/nkbs/meteo/models/microhh',
        microhh_bin = '/home/nkbs/meteo/models/microhh/build_sp_dpfft_cpumpi/microhh',
        env_setup = '/home/nkbs/setup_env.sh',
        work_dir = '/scratch/nkbs/',
        archive_dir = '/scratch/nkbs/archive',
        backend = Local_backend,
        ),

    lumi = dict(
        project = lumi_project,
        partition = 'standard',
        post_partition = 'small',
        lfs_c = 16,
        lfs_s = '2M',
        gpt_path = '/users/stratumv/meteo/models/coefficients_veerman',
        microhh_path = '/users/stratumv/meteo/models/microhh',
        microhh_bin = '/users/stratumv/meteo/models/microhh/build_spdp_cpumpi/microhh',
        env_setup = '/users/stratumv/setup_rcemip_ii.sh',
        work_dir = f'/scratch/{lumi_project}/rcemip_ii',
        archive_dir = lumi_project.replace('project_', 'lumi-') + '-private:',
        backend = Rclone_backend,
        ),
    )

env = compute_env['lumi']


"""
Experiment specific settings.
"""
exp_1 = dict(name = 'mw295dt2p5',  short_name = 'e1', mean_sst = 295, delta_sst = 2.5 )
exp_2 = dict(name = 'mw300dt2p5',  short_name = 'e2', mean_sst = 300, delta_sst = 2.5 )
exp_3 = dict(name = 'mw300dt1p25', short_name = 'e3', mean_sst = 300, delta_sst = 1.25)

# Note: wall clock limit LUMI = 2 days.
# 800 m = ~4.9 SDPD = 9.8 d
# 400 m = ~3.6 SDPD = 7.2 d
# 200 m = ~1.4 SDPD = 2.8 d

grid_800 = dict(
    res = 800,
    itot = 7680,
    jtot = 512, 
    npx = 128,
    npy = 16,
    coarse_ratio_x = 4,
    coarse_ratio_y = 4,
    time_chunk = 5*24*3600,
    chunks_xy_c = dict(time=121, y=128, x=960),         # 59 MB/file, 2 files/var.
    chunks_xy = dict(time=120, y=256, x=384),           # 47 MB/file, 40 files/var.
    chunks_xz = dict(time=121, z=128, x=768),           # 47 MB/file, 10 files/var.
    chunks_dump_c = dict(time=120, z=128, y=32, x=24),  # 47 MB/file, 320 files/var.
    )

grid_400 = dict(
    res = 400,
    itot = 15360,
    jtot = 1024,
    npx = 128,
    npy = 32,
    coarse_ratio_x = 8,
    coarse_ratio_y = 8,
    time_chunk = 5*24*3600,
    chunks_xy_c = dict(time=121, y=128, x=960),         # 59 MB/file, 2 files/var.
    chunks_xy = dict(time=120, y=256, x=384),           # 47 MB/file, 160 files/var.
    chunks_xz = dict(time=121, z=128, x=768),           # 47 MB/file, 20 files/var.
    chunks_dump_c = dict(time=120, z=128, y=32, x=24),  # 47 MB/file, 320 files/var.
    )

grid_200 = dict(
    res = 200,
    itot = 30720,
    jtot = 2048,
    npx = 128,
    npy = 64,
    coarse_ratio_x = 16,
    coarse_ratio_y = 16,
    time_chunk = 1*24*3600,
    chunks_xy_c = dict(time=25, y=128, x=1920),         # 24 MB/file, 1 file/var.
    chunks_xy = dict(time=24, y=512, x=1024),           # 50 MB/file, 120 files/var.
    chunks_xz = dict(time=25, z=128, x=3840),           # 47 MB/file, 8 files/var.
    chunks_dump_c = dict(time=24, z=128, y=64, x=64),   # 50 MB/file, 60 files/var.
    )

# Base setup of all RCEMIP-II experiments, combined with perturbations above.
rcemip_ii_base = dict(
    sw_cos_sst = True,
    ps = 101480,
    xsize = 6000_000,
    ysize = 400_000,
    end_time = 150*24*3600,
    wc_time = '48:00:00',
    post_cpus = 6,
    post_wc_time = '04:00:00',
    cleanup = True,
    start_xy_c = 0,
    start_xz = 0,
    start_dump_c = 125*24*3600,
    start_xy = 145*24*3600,
    restart_freq = 1*24*3600,
    restart_archive = 25*24*3600,
    iotimeprec = 1,
    )

def rcemip_ii_exp(exp, grid):
    """
    Create names for:
    - experiment (folder): e.g. `mw295dt2p5_800`
    - queue: e.g. `r8e1` (needs to be short!)
    Returns single dict for experiment.
    """
    name = exp['name']
    short_name = exp['short_name']
    res = grid['res']

    name = f'{name}_{res}'
    short_name = f'r{res//100}{short_name}'

    return rcemip_ii_base | grid | exp | dict(name=name, short_name=short_name)


experiments = dict(

    # RCEMIP-II, 800 m:
    rceii_800_e1 = rcemip_ii_exp(exp_1, grid_800),
    rceii_800_e2 = rcemip_ii_exp(exp_2, grid_800),
    rceii_800_e3 = rcemip_ii_exp(exp_3, grid_800),

    # RCEMIP-II, 400 m:
    rceii_400_e1 = rcemip_ii_exp(exp_1, grid_400),
    rceii_400_e2 = rcemip_ii_exp(exp_2, grid_400),
    rceii_400_e3 = rcemip_ii_exp(exp_3, grid_400),

    # RCEMIP-II, 200 m:
    rceii_200_e1 = rcemip_ii_exp(exp_1, grid_200),
    rceii_200_e2 = rcemip_ii_exp(exp_2, grid_200),
    rceii_200_e3 = rcemip_ii_exp(exp_3, grid_200),

    # RCEMIP-I:
    rcemip = dict(
        name = 'rcemip-i',
        short_name = 'rce1',
        mean_sst = 300,
        delta_sst = 2.5,
        sw_cos_sst = False,
        ps = 101480,
        xsize = 256*400,
        ysize = 256*400,
        itot = 256,
        jtot = 256,
        npx = 16,
        npy = 16,
        coarse_ratio_x = 8,
        coarse_ratio_y = 8,
        end_time = 4*24*3600,
        time_chunk = 4*24*3600,
        wc_time = '48:00:00',
        post_cpus = 6,
        post_wc_time = '04:00:00',
        cleanup = False,
        chunks_xy_c = dict(time=10_000, y=32, x=32),
        chunks_xy = dict(time=10_000, y=256, x=256),
        chunks_xz = dict(time=10_000, z=128, x=256),
        chunks_dump_c = dict(time=10_000, z=128, y=32, x=32),
        start_xy_c = 0,
        start_xz = 0,
        start_dump_c = 0*24*3600,
        start_xy = 0*24*3600,
        restart_freq = 1*24*3600,
        restart_archive = 4*24*3600,
        iotimeprec = 1,
        ),

    # Mirjam's quick test setup.
    rcemip_c = dict(
        name = 'rcemip_c',
        short_name = 'rcec',
        mean_sst = 300,
        delta_sst = -1,
        sw_cos_sst = False,
        ps = 101480,
        xsize = 128*1000,
        ysize = 128*1000,
        itot = 128,
        jtot = 128,
        npx = 8,
        npy = 16,
        coarse_ratio_x = 4,
        coarse_ratio_y = 4,
        end_time = 10*24*3600,
        time_chunk = 10*24*3600,
        wc_time = '12:00:00',
        post_cpus = 6,
        post_wc_time = '01:00:00',
        cleanup = False,
        chunks_xy_c = dict(time=10_000, y=8, x=32),
        chunks_xy = dict(time=10_000, y=32, x=128),
        chunks_xz = dict(time=10_000, z=128, x=128),
        chunks_dump_c = dict(time=10_000, z=128, y=8, x=32),
        start_xy_c = 0,
        start_xz = 0,
        start_dump_c = 0,
        start_xy = 0,
        restart_freq = 24*3600,
        restart_archive = 10*24*3600,
        iotimeprec = 0,
        ),

    # Small domain for development testing.
    dev = dict(
        name = 'dev',
        short_name = 'dev',
        mean_sst = 300,
        delta_sst = 1.25,
        sw_cos_sst = True,
        ps = 101480,
        xsize = 128*400,
        ysize = 64*400,
        itot = 128,
        jtot = 64,
        npx = 16,
        npy = 8,
        coarse_ratio_x = 8,
        coarse_ratio_y = 8,
        end_time = 2*24*3600,
        time_chunk = 24*3600,
        wc_time = '24:00:00',
        post_cpus = 6,
        post_wc_time = '01:00:00',
        cleanup = False,
        chunks_xy_c = dict(time=10_000, y=8, x=32),
        chunks_xy = dict(time=10_000, y=32, x=128),
        chunks_xz = dict(time=10_000, z=128, x=128),
        chunks_dump_c = dict(time=10_000, z=128, y=8, x=32),
        start_xy_c = 0,
        start_xz = 0,
        start_dump_c = 0,
        start_xy = 0,
        restart_freq = 12*3600,
        restart_archive = 24*3600,
        iotimeprec = 0,
        ),
    )


print('Hacking RCEMIP-II setup for test...')
exp = experiments['rceii_800_e1']
exp['end_time'] = 24*3600
exp['time_chunk'] = 24*3600
exp['restart_freq'] = 24*3600
exp['restart_archive'] = 24*3600
exp['start_dump_c'] = 0
exp['start_xy'] = 0
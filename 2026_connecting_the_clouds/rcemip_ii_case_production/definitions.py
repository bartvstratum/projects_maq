from filesystem_backend import Local_backend

"""
Compute environments.
Make sure all paths are ABSOLUTE!
"""
compute_env = dict(
    eddy = dict(
        project = None,
        partition = None,
        post_partition = None,
        lfs_c = None,
        lfs_s = None,
        gpt_path = '/home/bart/meteo/models/coefficients_veerman/',
        microhh_path = '/home/bart/meteo/models/microhh/',
        microhh_bin = '/home/bart/meteo/models/microhh/build_sp_gpu/microhh',
        #microhh_bin = '/home/bart/meteo/models/microhh/build_spdp_cpumpi/microhh',
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
        work_dir = '/scratch/nkbs/',
        archive_dir = '/scratch/nkbs/archive',
        backend = Local_backend,
        ),
    )

env = compute_env['eddy']


"""
Experiment specific settings.
"""
one_day = 24*3600


experiments = dict(

    # RCEMIP-I:
    rcemip = dict(
        name = 'rcemip-i',
        short_name = 'rcemip',
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
        end_time = 16*24*3600,
        time_chunk = 4*24*3600,
        wc_time = '48:00:00',
        post_cpus = 6,
        post_wc_time = '04:00:00',
        chunks_xy_c = (10_000, 32, 32),
        chunks_xy = (10_000, 256, 256),
        chunks_xz = (10_000, 128, 256),
        chunks_dump_c = (10_000, 128, 32, 32),
        start_xy_c = 0,
        start_xz = 0,
        start_dump_c = 8*24*3600,
        start_xy = 12*24*3600,
        ),

    # Small domain for development testing.
    dev = dict(
        name = 'dev',
        short_name = 'dev',
        mean_sst = 300,
        delta_sst = 1.25,
        sw_cos_sst = True,
        ps = 101480,
        xsize = 64*400,
        ysize = 32*400,
        itot = 64,
        jtot = 32,
        npx = 1,
        npy = 1,
        coarse_ratio_x = 4,
        coarse_ratio_y = 4,
        end_time = 10800,
        time_chunk = 3600,
        wc_time = '24:00:00',
        post_cpus = 6,
        post_wc_time = '01:00:00',
        chunks_xy_c = (10_000, 8, 32),
        chunks_xy = (10_000, 32, 128),
        chunks_xz = (10_000, 128, 128),
        chunks_dump_c = (10_000, 128, 8, 32),
        start_xy_c = 0,
        start_xz = 0,
        start_dump_c = 3600,
        start_xy = 7200,
        ),
    )

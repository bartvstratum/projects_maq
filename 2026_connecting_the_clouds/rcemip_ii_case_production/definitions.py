"""
Compute environments.
Make sure all paths are ABSOLUTE!
"""
compute_env = dict(
    eddy = dict(
        project = None,
        partition = None,
        lfs_c = None,
        lfs_s = None,
        gpt_path = '/home/bart/meteo/models/coefficients_veerman/',
        microhh_path = '/home/bart/meteo/models/microhh/',
        #microhh_bin = '/home/bart/meteo/models/microhh/build_sp_gpu/microhh',
        microhh_bin = '/home/bart/meteo/models/microhh/build_spdp_cpumpi/microhh',
        work_dir = '/home/bart/meteo/projects_maq/2026_connecting_the_clouds/rcemip_ii_case_production/experiments',
        archive_dir = '/home/bart/meteo/projects_maq/2026_connecting_the_clouds/rcemip_ii_case_production/archive'
        ),

    ecmwf = dict(
        project = None,
        partition = 'par',
        lfs_c = None,
        lfs_s = None,
        gpt_path = '/home/nkbs/meteo/models/coefficients_veerman',
        microhh_path = '/home/nkbs/meteo/models/microhh',
        microhh_bin = '/home/nkbs/meteo/models/microhh/build_sp_dpfft_cpumpi/microhh',
        work_dir = '/scratch/nkbs/',
        archive_dir = '/scratch/nkbs/archive',
        ),
    )

env = compute_env['eddy']


"""
Experiment specific settings.
"""
experiments = dict(

    # RCEMIP-I:
    rcemip = dict(
        name = 'rcemip_1',
        short_name = 'rcemip',
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
        coarse_ratio_y = 16,
        end_time = 20*24*3600,
        time_chunk = 10*24*3600,
        wc_time = '48:00:00',
        ),

    # Small domain for development testing.
    dev = dict(
        name = 'dev',
        short_name = 'dev',
        mean_sst = 300,
        delta_sst = 1.25,
        sw_cos_sst = True,
        ps = 101480,
        xsize = 256*400,
        ysize = 64*400,
        itot = 256,
        jtot = 32,
        npx = 1,
        npy = 1,
        coarse_ratio_x = 4,
        coarse_ratio_y = 4,
        end_time = 2*24*3600,
        time_chunk = 24*3600,
        wc_time = '12:00:00',
        chunks_xy_c = (10_000, 8, 64),
        chunks_xy = (10_000, 32, 256),
        chunks_xz = (10_000, 128, 256),
        chunks_dump_c = (10_000, 128, 8, 64),
        ),

    # Small domain for testing output.
    test = dict(
        name = '800m_small',
        short_name = 'd8s',
        mean_sst = 300,
        delta_sst = 1.25,
        sw_cos_sst = True,
        ps = 101480,
        xsize = 1920*800,
        ysize = 256*800,
        itot = 1920,
        jtot = 256,
        npx = 32,
        npy = 16,
        coarse_ratio_x = 4,
        coarse_ratio_y = 4,
        end_time = 4*24*3600,
        time_chunk = 2*24*3600,
        wc_time = '48:00:00',
        chunks_xy_c = (10_000, 64, 480),
        chunks_xy = (25, 256, 1920),
        chunks_xz = (10_000, 128, 1920),
        chunks_dump_c = (3, 128, 64, 480),
        ),

    # Small domain for testing output.
    budget = dict(
        name = 'budget_check',
        short_name = 'budget',
        mean_sst = 300,
        delta_sst = 1.25,
        sw_cos_sst = True,
        ps = 101480,
        xsize = 1920*800,
        ysize = 256*800,
        itot = 32,
        jtot = 32,
        npx = 2,
        npy = 4,
        coarse_ratio_x = 4,
        coarse_ratio_y = 4,
        end_time = 24*3600,
        time_chunk = 24*3600,
        wc_time = '48:00:00',
        chunks_xy_c = (10_000, 8, 8),
        chunks_xy = (10_000, 32, 32),
        chunks_xz = (10_000, 128, 32),
        chunks_dump_c = (3, 128, 8, 8),
        ),
    )

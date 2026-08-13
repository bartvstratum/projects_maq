"""
Compute environments.
"""
compute_env = dict(
    eddy = dict(
        project = None,
        partition = None,
        lfs_c = None,
        lfs_s = None,
        gpt_path = '/home/bart/meteo/models/coefficients_veerman/',
        microhh_path = '/home/bart/meteo/models/microhh/',
        microhh_bin = '/home/bart/meteo/models/microhh/build_sp_gpu/microhh',
        work_dir = 'experiments/'
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
        ),
    )

env = compute_env['ecmwf']


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

    # Small test domain:
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
        npx = 32,
        npy = 4,
        coarse_ratio_x = 4,
        coarse_ratio_y = 4,
        end_time = 3*24*3600,
        time_chunk = 24*3600,
        wc_time = '12:00:00',
        ),

    mini = dict(
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
        end_time = 3*24*3600,
        time_chunk = 24*3600,
        wc_time = '48:00:00',
        ),
    )

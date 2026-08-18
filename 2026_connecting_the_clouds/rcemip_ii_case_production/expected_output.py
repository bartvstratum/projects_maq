vars_xy = dict(
    rrsg_bot          = ('000', None),
    thl_fluxbot       = ('000', None),
    qt_fluxbot        = ('000', None),
    lw_flux_dn        = ('001', (0, 128)),
    lw_flux_up        = ('001', (0, 128)),
    sw_flux_dn        = ('001', (0, 128)),
    sw_flux_up        = ('001', (0, 128)),
    sw_flux_dn_clear  = ('001', (0, 128)),
    sw_flux_up_clear  = ('001', (0, 128)),
    lw_flux_dn_clear  = ('001', (0, 128)),
    lw_flux_up_clear  = ('001', (0, 128)),
    qt_path           = ('000', None),
    qsat_path         = ('000', None),
    qlqi_path         = ('000', None),
    qi_path           = ('000', None),
    t2m               = ('000', None),
    u10m              = ('100', None),
    v10m              = ('010', None),
    thl               = ('000', (0,)),
    u                 = ('100', (0,)),
    v                 = ('010', (0,)),
    w500hpa           = ('000', None),
)

vars_xz = dict(
    thl = '000',
    qt  = '000',
    ql  = '000',
    qi  = '000',
    qr  = '000',
    qs  = '000',
    qg  = '000',
    u   = '100',
    w   = '001',
)

vars_dump_c = dict(
    u              = '100',
    v              = '010',
    w              = '001',
    thl            = '000',
    qt             = '000',
    ql             = '000',
    qi             = '000',
    qr             = '000',
    qs             = '000',
    qg             = '000',
    qlqi_mask      = '000',
    thl_tend       = '000',
    qt_tend        = '000',
    w_tend         = '001',
    thl_tend_lw    = '000',
    thl_tend_sw    = '000',
    qrsg_tend_sed  = '000',
    qtr_tend_frz   = '000',
    uthl           = '100',
    vthl           = '010',
    wthl           = '001',
    uqt            = '100',
    vqt            = '010',
    wqt            = '001',
    wqr            = '001',
    wql            = '001',
    wqi            = '001',
    uw             = '101',
    vw             = '011',
)


def expected_zarr_relpaths():
    relpaths = {}

    for kind in ('xy_c', 'xy'):
        paths = []
        for var, (_, z_indices) in vars_xy.items():
            if z_indices is None:
                paths.append(f'{var}.zarr')
            else:
                for z in z_indices:
                    paths.append(f'{var}_{z}.zarr')
        relpaths[kind] = sorted(paths)

    relpaths['xz'] = sorted(f'{var}_ymean.zarr' for var in vars_xz)
    relpaths['3d_c'] = sorted(f'{var}.zarr' for var in vars_dump_c)

    return relpaths

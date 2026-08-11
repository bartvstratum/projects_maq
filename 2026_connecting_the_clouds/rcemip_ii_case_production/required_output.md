## Required output production runs

### Summary:

- Restart files: archive every 25d
- Cross xy native: hourly, last 5d
- Cross xy coarse: hourly, full sim
- Cross xz native: hourly, full sim (spanwise mean)
- Reduced 3D: hourly, last 25d

### Restart files

- Archived every 25 simulated days.
- Output frequency = restart chunk time? 

### Cross-sections, full resolution.

> 2D fields in XY and XZ will comprise the fields listed in Table A3 of the RCEMIP-II protocol10

- [x] pr Surface precipitation rate kg m−2 s−1 --> rrsg_bot
- [x] hﬂs Surface upward latent heat ﬂux W m−2 --> thl_fluxbot, needs post for conversion
- [x] hfss Surface upward sensible heat ﬂux W m−2 --> qt_fluxbot, needs post for conversion
- [x] rlds Surface downwelling longwave ﬂux W m−2 --> lw_flux_dn
- [x] rlus Surface upwelling longwave ﬂux W m−2 --> lw_flux_up
- [x] rsds Surface downwelling shortwave ﬂux W m−2 --> sw_flux_dn
- [x] rsus Surface upwelling shortwave ﬂux W m−2 --> sw_flux_up
- [x] rsdscs Surface downwelling shortwave ﬂux – clear sky W m−2 --> sw_flux_dn_clear
- [x] rsuscs Surface upwelling shortwave ﬂux – clear sky W m−2 --> sw_flux_up_clear
- [x] rldscs Surface downwelling longwave ﬂux – clear sky W m−2 --> lw_flux_dn_clear
- [x] rluscs Surface upwelling longwave ﬂux – clear sky W m−2 --> lw_flux_up_clear
- [x] rsdt TOA incoming shortwave ﬂux W m−2 -> TOD sw_flux_dn
- [x] rsut TOA outgoing shortwave ﬂux W m−2 -> TOD sw_flux_up, needs post to add TOD to TOA
- [x] rlut TOA outgoing longwave ﬂux W m−2 -> TOD lw_flux_up, needs post to add TOD to TOA
- [x] rsutcs TOA outgoing shortwave ﬂux – clear sky W m−2 -> sw_flux_up_clear, needs post to add TOD to TOA
- [x] rlutcs TOA outgoing longwave ﬂux – clear sky W m−2 -> lw_flux_up_clear, needs post to add TOD to TOA
- [x] prw Water vapor path kg m−2 --> **NOTE** replaced by qt_path -> qt_path - qlqi_path = qv_path.
- [x] sprw Saturated water vapor path kg m−2 --> qsat_path
- [x] clwvi Condensed water path (cloud ice + cloud liquid) kg m−2 --> qlqi_path
- [x] clivi Ice water path (cloud ice) kg m−2 --> qi_path
- [ ] psl Sea level pressure Pa --> **NOTE** = constant in LES (1D phydro) or 3D phydro?
- [x] tas 2 m air temperature K --> t2m
- [x] tabot Air temperature at lowest model level K --> thl, needs post for conversion
- [x] uas 10 m eastward wind m s−1 --> u10m
- [x] vas 10 m northward wind m s−1 --> v10m
- [x] uabot Eastward wind at lowest model level m s−1 --> u
- [x] vabot Northward wind at lowest model level m s−1 --> v
- [x] wa500 or wap500 Vertical velocity or omega at 500 hPa m s−1 or Pa s−1 --> w500hpa
- [ ] cl! Total cloud fraction of grid column --> **NOTE** 1/0 in LES, can be calculated as qlqi_path mask
- [ ] pr_conv! Surface convective precipitation rate kg m−2 s−1 **NOTE** == does not exist in LES.
- [ ] albisccp! ISCCP mean cloud albedo **NOTE** Needs to be implemented?
- [ ] cltisccp! ISCCP total cloud cover % **NOTE** Needs to be implemented?
- [ ] pctisccp! ISCCP mean cloud-top pressure Pa **NOTE** Needs to be implemented?

```
crosslist = rrsg_bot,thl_fluxbot,qt_fluxbot,lw_flux_dn,lw_flux_up,sw_flux_dn,sw_flux_up,sw_flux_dn_clear,sw_flux_up_clear,lw_flux_dn_clear,lw_flux_up_clear,qt_path,qsat_path,qlqi_path,qi_path,t2m,u10m,v10m,thl,u,v,w500hpa
```

**NOTES**:
- qr_path not in output?
- Diagnostic MO includes t2m, u10m, v10m, but not q2m?
- For XZ, output only thl + u + v.
- Do we want spanwise averaged cross-sections of e.g. thl, qt, ql, qi, qr, qs, qg, u, w, ...?

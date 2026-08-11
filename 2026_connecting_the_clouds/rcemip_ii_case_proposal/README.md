# RCEMIP-II MicroHH case.

RCEMIP-II / mock-Walker circulation setup from [Wing et al. (2024)](https://doi.org/10.5194/gmd-17-6195-2024).

## NOTES

- To restart from an interpolated low resolution simulation, follow the order:
  - run `rcemip_ii_input.py` to generate the default case input for the hi-res case.
  - run the `init` phase of MicroHH to generate the grid definition, FFT plan, et cetera. 
  - run `regrid.py` to overwrite the homogeneous 2D/3D fields created by `init`.
  - run the `run` phase to start the warm start.

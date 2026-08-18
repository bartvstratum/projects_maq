# Production RCEMIP-II case

## Overview files / workflow:

**Main settings:**
- `definitions.py`: defines the HPCs, file paths, and experiment settings.
- `expected_output.py`: defines which output is converted to Zarr and archived.

**Main workflow:**
- `generate_case.py` creates/copies the input needed for a single experiment: initial profiles, `.ini` file, 2D SST input, MicroHH executable, RRTMGP lookup tables, etc.
- `submit_chunks.py` chunks the experiment in time, and daisy-chains all chunks including pre- and postprocessing steps using SLURM.

**Help scripts** (typically not manually invoked):
- `convert_bin_to_zarr.py`: converts all MicroHH binaries to Zarr archives.
- `archive.py`: archives the Zarr archives and other output.
- `case_setup.py`: defines basic RCEMIP I/II setup.

- `prepare_ini.py`: updates `.ini` file before each time chunk.

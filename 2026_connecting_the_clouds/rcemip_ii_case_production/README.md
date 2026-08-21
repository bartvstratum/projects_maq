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

## LUMI-O
- Generate credentials at https://auth.lumidata.eu/
- `module load lumio` -> run `lumio-conf` and feed the access and secret keys.

## LUMI environment

The automated runs source a bash script to load the correct modules. `setup_rcemip_ii.sh`:

    module --force purge
    module load LUMI/25.03
    module load partition/C
    module load Boost/1.88.0-cpeCray-25.03
    module load Szip/2.1.1-cpeCray-25.03
    module load cray-hdf5
    module load cray-netcdf
    module load cray-fftw
    module load cray-python
    module load lumio
    module load lumi-tools

    source ~/venvs/rcemip_ii/bin/activate

To setup the virtual environment:

    python -m venv ~/venvs
    source ~/venvs/rcemip_ii/bin/activate
    pip install -r requirements.txt

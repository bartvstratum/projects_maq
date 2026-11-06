# Reading LUMI-O data remotely
 
## Setup
 
1. At <https://auth.lumidata.eu>, create a key and generate the configuration template for **shell**.
2. Save it somewhere outside the repo (e.g. `~/setup_lumi_o.sh`), and source it before starting Python, Jupyter or rclone:
```bash
   source ~/setup_lumi_o.sh
```
 
3. `pip install s3fs xarray zarr`
## Use
 
List the buckets and their contents with rclone:
 
```bash
rclone lsd lumio:
rclone lsd lumio:mw300dt2p5-800/chunk_001
rclone ls  lumio:mw300dt2p5-800/chunk_001/logs
```
 
In Python, `lumio:mw300dt2p5-800/...` becomes `s3://mw300dt2p5-800/...`:
 
```python
import os
import s3fs
import xarray as xr
 
opts = {
    'client_kwargs': {'endpoint_url': os.environ['AWS_ENDPOINT_URL']},
    'use_listings_cache': False,
}
fs = s3fs.S3FileSystem(**opts)
 
# Log file
print(fs.cat('mw300dt2p5-800/chunk_001/logs/r8e2_r01.out').decode())
 
# One Zarr
ds = xr.open_zarr('s3://mw300dt2p5-800/chunk_001/xy/qlqi_path.zarr', storage_options=opts)
 
# All chunks
paths = ['s3://' + p for p in sorted(fs.glob('mw300dt2p5-800/chunk_*/xy/qlqi_path.zarr'))]
ds = xr.open_mfdataset(paths, engine='zarr', combine='by_coords', storage_options=opts)
```

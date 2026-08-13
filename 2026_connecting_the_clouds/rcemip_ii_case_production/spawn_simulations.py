import numpy as np
import argparse

from definitions import experiments, compute_env

"""
Different systems for testing...
"""
# Snellius:
account = None
partition = 'rome'
lfs_s = None
lfc_s = None


"""
Parse cmd line arguments.
"""
parser = argparse.ArgumentParser()
parser.add_argument('--experiment', required=True, help='Experiment name')
parser.add_argument('--system', required=True, help='HPC name')
parser.add_argument('--time_chunk', type=int, required=True)
parser.add_argument('--wc_time', type=str, default='48:00:00')
args = parser.parse_args()

if len(args.identifier) > 6:
    raise Exception('SLURM identifier needs to be short, max 6 chars')


"""
Spawn simulations chunks, daisy-chained through their SLURM IDs.
"""
n_chunks = int(np.ceil(args.total_time / args.time_chunk))

print(f'Dividing {args.total_time} into {n_chunks} runs of {args.time_chunk}...')

for i in range(n_chunks):
    start_time = i * args.time_chunk
    end_time = (i+1) * args.time_chunk
    end_time = min(end_time, args.total_time)

    name = f'{args.identifier}{i:02d}'

    """
    Create SLURM script.
    """
    slurm_script = f'{args.work_dir}/chunk_{i}.slurm'
    with open(slurm_script, 'w') as f:

        f.write(f'#!/bin/bash\n\n')
        if account is not None:
            f.write(f'#SBATCH --account={account}\n')
        f.write(f'#SBATCH --job-name={name\n')
        f.write(f'#SBATCH --output={args.work_dir}/name-%j.out\n')
        f.write(f'#SBATCH --error={args.work_dir}/name-%j.err\n')
        f.write(f'#SBATCH --partition={partition}\n')
        f.write(f'#SBATCH --ntasks={npx*npy}\n')

        if partition == 'gpu_h100' or partition == 'gpu_a100':
            f.write(f'#SBATCH --cpus-per-task=16\n')
            f.write(f'#SBATCH --gpus-per-node=1\n')
        else:
            f.write(f'#SBATCH --cpus-per-task=1\n')

        f.write(f'#SBATCH --ntasks-per-core=1\n')

        if partition == 'standard':
            f.write(f'#SBATCH --mem=224G\n')

        f.write(f'#SBATCH --time={args.wc_time}\n\n')
        f.write(f'source ~/setup_env.sh\n\n')

        f.write(f'cd {args.work_dir}\n\n')

        f.write(f'python prepare_ini.py --work_dir={args.work_dir} --start_time={start_time} --end_time={end_time} --total_time={total_time}'

        if partition == 'standard':
            f.write('export FI_CXI_RX_MATCH_MODE=hybrid\n\n')

        if lfs_c is not None and lfs_s is not None:
            f.write(f'lfs setstripe -c {lfs_c} -S {lfs_s} {work_dir}\n\n')

        if start_time == 0:
            f.write(f'srun ./microhh init rcemip_ii\n')
        f.write(f'srun ./microhh run rcemip_ii\n\n')


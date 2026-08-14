import os
import argparse
import subprocess

import numpy as np

from definitions import experiments, env

script_dir = os.path.dirname(os.path.abspath(__file__))


"""
Parse cmd line arguments.
"""
parser = argparse.ArgumentParser()
parser.add_argument('--exp', required=True, help='Experiment name')
args = parser.parse_args()

"""
Experiment settings.
"""
exp = experiments[args.exp]

# Short name used for identifying runs in SLURM queue. 6 chars + chunk id.
identifier = exp['short_name']
if len(identifier) > 6:
    raise Exception('SLURM identifier needs to be short, max 6 chars')

# Local short-cuts.
total_time = exp['end_time']
time_chunk = exp['time_chunk']
wc_time = exp['wc_time']
work_dir = os.path.abspath(os.path.join(env['work_dir'], exp['name']))

npx = exp['npx']
npy = exp['npy']

account = env['project']
partition = env['partition']
lfs_c = env['lfs_c']
lfs_s = env['lfs_s']


"""
Spawn simulations chunks, daisy-chained through their SLURM IDs.
"""
n_chunks = int(np.ceil(total_time / time_chunk))

print(f'Dividing {total_time} into {n_chunks} runs of {time_chunk}...')

previous_job_id = None

for i in range(n_chunks):
    start_time = i * time_chunk
    end_time = (i+1) * time_chunk
    end_time = min(end_time, total_time)

    name = f'{identifier}{i:02d}'

    def create_slurm_script():
        """
        Create and submit SLURM script.
        """
        global previous_job_id

        slurm_script = f'{work_dir}/chunk_{i}.slurm'
        with open(slurm_script, 'w') as f:

            f.write(f'#!/bin/bash\n\n')
            if account is not None:
                f.write(f'#SBATCH --account={account}\n')
            f.write(f'#SBATCH --job-name={name}\n')
            f.write(f'#SBATCH --output={work_dir}/{name}-%j.out\n')
            f.write(f'#SBATCH --error={work_dir}/{name}-%j.err\n')
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
            f.write(f'#SBATCH --time={wc_time}\n\n')

            f.write(f'source ~/setup_env.sh\n\n')

            f.write(f'cd {work_dir}\n\n')

            f.write(f'python {script_dir}/prepare_ini.py --exp={args.exp} --start_time={start_time} --end_time={end_time}\n\n')

            if partition == 'standard':
                f.write('export FI_CXI_RX_MATCH_MODE=hybrid\n\n')

            if lfs_c is not None and lfs_s is not None:
                f.write(f'lfs setstripe -c {lfs_c} -S {lfs_s} {work_dir}\n\n')

            if start_time == 0:
                f.write(f'srun ./microhh init rcemip_ii\n')
            f.write(f'srun ./microhh run rcemip_ii\n\n')

            # TODO: post-processing + archiving.

        """
        Submit SLURM script, daisy-chained onto the previous chunk with `afterok`.
        """
        sbatch_cmd = ['sbatch', '--parsable']
        if previous_job_id is not None:
            sbatch_cmd.append(f'--dependency=afterok:{previous_job_id}')
        sbatch_cmd.append(slurm_script)

        result = subprocess.run(sbatch_cmd, capture_output=True, text=True, check=True)
        previous_job_id = result.stdout.strip()

        print(f'Submitted chunk {i} ({name}) as job {previous_job_id}')


    def create_bash_script():
        """
        Create simple bash script for local testing.
        """
        bash_script = f'{work_dir}/chunk_{i}.sh'
        with open(bash_script, 'w') as f:

            f.write(f'#!/bin/bash\n\n')
            f.write(f'cd {work_dir}\n\n')
            f.write(f'python {script_dir}/prepare_ini.py --exp={args.exp} --start_time={start_time} --end_time={end_time}\n\n')
            if start_time == 0:
                f.write(f'./microhh init rcemip_ii\n')
            f.write(f'./microhh run rcemip_ii\n\n')

        os.chmod(bash_script, 0o755)


    if partition is None:
        create_bash_script()
    else:
        create_slurm_script()

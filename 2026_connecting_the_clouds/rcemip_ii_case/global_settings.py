#
#  MicroHH
#  Copyright (c) 2011-2024 Chiel van Heerwaarden
#  Copyright (c) 2011-2024 Thijs Heus
#  Copyright (c) 2014-2024 Bart van Stratum
#
#  This file is part of MicroHH
#
#  MicroHH is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  MicroHH is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with MicroHH.  If not, see <http://www.gnu.org/licenses/>.
#

system = 'snellius'

if system == 'eddy':
    project = None
    partition = None
    gpt_path = '/home/bart/meteo/models/coefficients_veerman/' 
    microhh_path = '/home/bart/meteo/models/microhh/'
    microhh_bin = '/home/bart/meteo/models/microhh/build_sp_cpumpi/microhh'
    work_dir = 'test_200m'

elif system == 'snellius':  # MAQ account
    project = None
    partition = 'gpu_h100'
    gpt_path = '/gpfs/work3/0/lesmodels/team_bart/coefficients_veerman'
    microhh_path = '/home/bstratum/meteo/models/microhh'
    microhh_bin = '/home/bstratum/meteo/models/microhh/build_sp_gpu_kl/microhh'
    work_dir = '/scratch-shared/bstratum/rcemip-ii_resolution'

elif system == 'snellius2':  # Ruisdael account
    project = None
    partition = 'rome'
    gpt_path = '/home/bvstratum/meteo/models/coefficients_veerman'
    microhh_path = '/home/bvstratum/meteo/models/microhh'
    microhh_bin = '/home/bvstratum/meteo/models/microhh/build_spdp_cpumpi/microhh'
    work_dir = '/scratch-shared/bvstratum/rcemip_ii_800m'

elif system == 'ecmwf':
    project = None
    partition = 'par'
    gpt_path = '/home/nkbs/meteo/models/coefficients_veerman'
    microhh_path = '/home/nkbs/meteo/models/microhh'
    microhh_bin = '/home/nkbs/meteo/models/microhh/build_sp_dpfft_cpumpi/microhh'
    work_dir = '/scratch/nkbs/mock_walker_xl_400m'

elif system == 'lumi':
    project = 'project_465002576'
    partition = 'standard'
    gpt_path = '/users/stratumv/meteo/models/coefficients_veerman'
    microhh_path = '/users/stratumv/meteo/models/microhh'
    microhh_bin = '/users/stratumv/meteo/models/microhh/build_spdp_cpumpi/microhh'
    work_dir = f'/scratch/{project}/mock_walker_scaling_v3'

    # Default serial I/O (single task) for cross-sections.
    #microhh_bin = '/users/stratumv/meteo/models/microhh/build_spdp_cpumpi_serialio/microhh'
    #work_dir = f'/scratch/{project}/mock_walker_serialio'

    # Test with MPI I/O for all output incl cross-sections.
    #microhh_bin = '/users/stratumv/meteo/models/microhh/build_spdp_cpumpi_mpiio/microhh'
    #work_dir = f'/scratch/{project}/mock_walker_mpiio'

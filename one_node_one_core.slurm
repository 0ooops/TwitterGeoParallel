#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=00:10:00

# Load required modules
module load Python/3.4.3-goolf-2015a

# Launch multiple process python code
echo "Time for 1 node 1 core: "
time mpiexec -n 1 python gridAllocation_big_one_core.py

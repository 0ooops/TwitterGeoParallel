#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=00:10:00

# Load required modules
module load Python/3.4.3-goolf-2015a

# Launch multiple process python code
echo "Time for 1 node 8 cores: "
time mpiexec -n 8 python gridAllocation_big_peer.py

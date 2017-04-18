# Purpose
This package is used for parsing and calculating Twitter geographical data by using different methods and resouces.

# Content
The package contains folowing files:
1. gridAllocation_big_one_core.py   --for running on one process 
   (You may also use below two files to test one-core-one-node, but it's meaningless to MPI.send or MPI.scatter from one process to itself. 
   I reconstruct this file just to save useless transmission time and make a better comparison. The computing methods are the same as below.)
2. gridAllocation_big_master.py  --implements a master/slave model for parallel computing
3. gridAllocation_big_peer.py  --implements peer based model for parallel computing
4. *.slurm  --for submitting jobs on Spartan
5. README.md

# Local Command
The below command is used to run these files locally on bash, shell or equivalent:

execmpi -n [number of processes] python [directory and file name]

# Scripts on Spartan
The below scrips is uesd to run these files on Spartan. You may also refer to the *.slurm files.

    #!/bin/bash
    #SBATCH --nodes=[number of nodes]
    #SBATCH --ntasks-per-node=[number of cores per node]
    #SBATCH --time=00:10:00

    # Load required modules
    module load Python/3.4.3-goolf-2015a

    # Launch multiple process python code
    echo "Time for [number of nodes] node [number of cores] cores: "
    time mpiexec -n [number of total cores]] python [directory and file name]

# Requirements
Please put melbGrid.json and bigTwitter.json at the same folder as *.py files before testing.

# Output
The output of each program is a list of ranked grid and twitter counts, ranked rows and ranked columns,
and the time used as a total and for preprocessing or transmission.
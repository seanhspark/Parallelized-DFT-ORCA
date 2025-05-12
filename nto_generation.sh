#!/bin/bash
#SBATCH --job-name=NTO
#SBATCH --account=rrg-aspuru
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --time=00:30:00
#SBATCH -p debug

# Set OMP and MKL properly
export OMP_NUM_THREADS=40
export MKL_NUM_THREADS=40

# Load modules
module --force purge
module load CCEnv
module load StdEnv/2020
module load scipy-stack
module load java/17.0.2
module load intel/2021.2.0
module load openmpi/4.1.1

export PATH=$SLURM_SUBMIT_DIR:$PATH
export OMP_STACKSIZE=3500M

export ORCAPATH=/project/a/aspuru/orca/orca503
export PATH=$PATH:$ORCAPATH
export THEODIR=/home/a/aspuru/seanpark/TheoDORE_3.1.1
export PATH=$THEODIR/bin:$PATH
export PYTHONPATH=$THEODIR:$PYTHONPATH
export RSH_COMMAND="/usr/bin/ssh"
export OMPI_MCA_mtl='^mxm'
export OMPI_MCA_pml='^yalla'

# Find directories and execute commands in parallel
find $base_dir -type d -regex ".*/nto_mulliken/[A-Z][A-Z][A-Z][0-9][0-9][0-9]" | parallel -j 40 bash -c '
    dir_path="{}"
    echo "Accessing directory: $dir_path"
    cd "$dir_path" || exit
    echo "Current directory: $(pwd)"
    name="${dir_path##*/}"  # Extracts the last part of the path
    $ORCAPATH/orca_2mkl $name -molden
    $THEODIR/bin/theodore analyze_tden
    cd -
'
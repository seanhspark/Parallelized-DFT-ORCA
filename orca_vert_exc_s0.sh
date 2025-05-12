#SBATCH --account=rrg-aspuru
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --time=04:00:00
##SBATCH -p debug

# Set OMP and MKL properly
export OMP_NUM_THREADS=40
export MKL_NUM_THREADS=40

# Load modules
module --force purge
module load NiaEnv/2019b
module load gcc/9.2.0
module load openmpi/4.1.1

export PATH=$SLURM_SUBMIT_DIR:$PATH
export OMP_STACKSIZE=3500M

export ORCAPATH=/project/a/aspuru/orca/orca503
export PATH=$PATH:$ORCAPATH
export RSH_COMMAND="/usr/bin/ssh"
export OMPI_MCA_mtl='^mxm'
export OMPI_MCA_pml='^yalla'


for file in *.in; do
        fname=$(basename -- "$file" .in)
        if { [ ! -e "$fname.out" ] && [ -e "$fname.in" ]; } || ls | grep -q "^$fname.*\.tmp$"; then
                $ORCAPATH/orca "$fname.in" > "$fname.log"
                mv "$fname.log" "$fname.out"
                echo "$fname.out" >> calculated_file
        fi
done


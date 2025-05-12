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
module load gnu-parallel/20191122
module load gcc/9.2.0
module load openmpi/4.1.1

export PATH=$SLURM_SUBMIT_DIR:$PATH
export OMP_STACKSIZE=3500M

export ORCAPATH=/project/a/aspuru/orca/orca503
export PATH=$PATH:$ORCAPATH
export RSH_COMMAND="/usr/bin/ssh"
export OMPI_MCA_mtl='^mxm'
export OMPI_MCA_pml='^yalla'


# Create a work directory in Ramdisk
workdir="/dev/shm/$USER/workdir"
mkdir -p $workdir

# Copy input files to the Ramdisk
cp $SLURM_SUBMIT_DIR/* $workdir

# Move to the work directory
cd $workdir


# for file in *.in; do
#         fname=$(basename -- "$file" .in)
#         if { [ ! -e "$fname.out" ] && [ -e "$fname.in" ]; } || ls | grep -q "^$fname.*\.tmp$"; then
#                 $ORCAPATH/orca "$fname.in" > "$fname.log"
#                 mv "$fname.log" "$fname.out"
#                 echo "$fname.out" >> calculated_file
#         fi
# done


# Extract the total walltime (in minutes) from SLURM environment variable
total_walltime_minutes=$((SLURM_JOB_TIMELIMIT))

# Calculate the timeout in seconds
# Let's subtract 2 minutes as a buffer from the walltime
timeout_minutes=$((total_walltime_minutes - 2))
timeout_seconds=$((timeout_minutes * 60))

# Set the timeout in hours (for readability), but ensure it doesn't exceed the total walltime
timeout_hours=$(($timeout_seconds / 3600))

# Command template using the dynamically calculated timeout
command_template='
        fname=$(basename -- "{}" .in)
        if { [ ! -e "$fname.out" ] && [ -e "$fname.in" ]; } || ls | grep -q "^$fname.*\.tmp$"; then
                timeout '"$timeout_hours"'h $ORCAPATH/orca "$fname.in" | tee "$fname.log" | tee "$SLURM_SUBMIT_DIR/$fname.log" > /dev/null
                if [ $? -ne 0 ]; then
                    # If timeout or error occurs, create a .tmp file
                    touch "$fname.tmp"
                else
                    # Move log file to output file, delete log and all .tmp files
                    mv "$fname.log" "$fname.out"
                    echo "$fname.out" >> calculated_file
                    rm -f "$SLURM_SUBMIT_DIR/$fname.log"
                    rm -f "$fname"*.tmp   # Delete all .tmp files matching $fname*.tmp
                fi
        fi
'

# Find all .in files in the current directory and execute the command_template on each using GNU Parallel
find . -maxdepth 1 -type f -name "*.in" | parallel -j 1 "
    $command_template
"

# Optionally, you can wait for all jobs to finish
wait

# Archive the output files and copy back to submit directory
tar --exclude='*tmp*' -cf $SLURM_SUBMIT_DIR/out.tar *

# Extract the archived files in the submission directory
cd $SLURM_SUBMIT_DIR
tar xf out.tar
rm out.tar

# Clean up the Ramdisk
rm -r $workdir

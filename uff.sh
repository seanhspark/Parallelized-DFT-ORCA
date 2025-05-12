#!/bin/bash
#SBATCH --job-name=uff
#SBATCH --account=rrg-aspuru
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --time=05:00:00
##SBATCH -p debug

export g16root="/project/a/aspuru/opt/gaussian"
gr=$g16root
export GAUSS_EXEDIR="$gr/g16C01/bsd:$gr/g16C01"
export GAUSS_LEXEDIR="$gr/g16C01/linda-exe"
export GAUSS_ARCHDIR="$gr/g16C01/arch"
export GAUSS_BSDDIR="$gr/g16C01/bsd"
export GAUSS_SCRDIR=$workdir # change to your scratch directory
export LD_LIBRARY_PATH="$GAUSS_EXEDIR:$LD_LIBRARY_PATH"
export PATH="$PATH:$gr/gauopen:$GAUSS_EXEDIR"

module --force purge
module load CCEnv
module load StdEnv/2020
module load scipy-stack

#g16 <$SLURM_SUBMIT_DIR/input.com>  $SLURM_SUBMIT_DIR/input.log
# DIRECTORY TO RUN - $SLURM_SUBMIT_DIR is directory job was submitted from
cd $SLURM_SUBMIT_DIR

for file in *.com; do
        fname=$(basename -- "$file" .com)
        if [ ! -e "$fname.out" ] && [ -e "$fname.com" ]; then
                g16 "$fname.com" "$fname.log"
                mv "$fname.log" "$fname.out"
                echo "$fname.out" >> calculated_file
        fi
done


cp $SLURM_SUBMIT_DIR/../out2xyz.py $SLURM_SUBMIT_DIR
/cvmfs/soft.computecanada.ca/easybuild/software/2020/avx512/Core/python/3.10.2/bin/python $SLURM_SUBMIT_DIR/out2xyz.py
cp $SLURM_SUBMIT_DIR/opt_xyz/*.xyz $SLURM_SUBMIT_DIR/../

rm -r $SLURM_SUBMIT_DIR

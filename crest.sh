#SBATCH --account=rrg-aspuru
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --time=12:00:00
##SBATCH -p debug

cat $SLURM_JOB_NODELIST
cd $SLURM_SUBMIT_DIR

# source ~/xtb-6.5.0/share/xtb/config_env.bash

export OMP_NUM_THREADS=40
export MKL_NUM_THREADS=40

ulimit -s unlimited

module --force purge
module load CCEnv
module load StdEnv/2020
module load crest/2.12

mkdir -p best_geom #conformers #for collecting the most stable conformer and conformers

command_template='
  file={}
  fname=$(basename -- "$file" .xyz)
  if [ ! -d "$fname" ]; then
    mkdir -p "$fname"
    cp "$fname.xyz" "$fname"
    cd "$fname"
    cp $SLURM_SUBMIT_DIR/constraints.inp .
    crest "$fname.xyz" --gfn2 --cinp constraints.inp --chg -1 --uhf 1 --mquick --noreftopo -T 16 > "$fname.log"
    mv "$fname.log" "$fname.out"
    cp crest_best.xyz $SLURM_SUBMIT_DIR/best_geom/$fname.xyz
    cd "$SLURM_SUBMIT_DIR"
  else
    if [ -e "$fname" ] && [ ! -e "$fname/$fname.out" ]; then
      cd "$fname"
      cp $SLURM_SUBMIT_DIR/constraints.inp .
      crest "$fname.xyz" --gfn2 --cinp constraints.inp --chg -1 --uhf 1 --mquick --noreftopo -T 16 > "$fname.log"
      mv "$fname.log" "$fname.out"
      cp crest_best.xyz $SLURM_SUBMIT_DIR/best_geom/$fname.xyz
      cd "$SLURM_SUBMIT_DIR"
    fi
  fi
'

# Find all .xyz files in the current directory and execute the command_template on each using GNU Parallel
find . -maxdepth 1 -type f -name "*.xyz" | parallel -j 2 "$command_template"

# Optionally, you can wait for all jobs to finish
wait


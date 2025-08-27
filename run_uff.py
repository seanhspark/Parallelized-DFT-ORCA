import numpy as np
import glob
import sys
import os
from tqdm import tqdm

# Check working directory
print("Current working directory:", os.getcwd())

# Check input files
if not os.path.exists('uff.in'):
    print("ERROR: 'uff.in' not found. Exiting.")
    sys.exit(1)

if not os.path.exists('uff.sh'):
    print("ERROR: 'uff.sh' not found. Exiting.")
    sys.exit(1)

# Read the template for the .in file
opt = open('uff.in').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'uff/'

print(f"Creating output directory: {INPDIR}")
os.makedirs(INPDIR, exist_ok=True)

# List all .xyz files in the GEOM_DIR
xyz_files = glob.glob(os.path.join(GEOM_DIR, '*.xyz'))

if not xyz_files:
    print("No .xyz files found in current directory. Exiting.")
    sys.exit(1)

print(f"Found {len(xyz_files)} .xyz files.")

# Generate .com files
for f in xyz_files:
    try:
        xyz = open(f).readlines()[2:]
    except Exception as e:
        print(f"Could not read {f}: {e}")
        continue
    nm = os.path.basename(f).split('.')[0]
    ginp = opt + [nm + '\n\n'] + ['0 1\n'] + xyz + ['\n']
    g16 = os.path.join(INPDIR, nm + '.com')
    with open(g16, 'w') as com_file:
        com_file.writelines(ginp)
    print(f"Wrote: {g16}")

# Copy and submit job
try:
    os.system(f"cp uff.sh {INPDIR}")
    os.chdir(INPDIR)
    print(f"Submitting SLURM job from {os.getcwd()}")
    os.system("sbatch uff.sh")
    os.system("rm uff.sh")
except Exception as e:
    print(f"Error during SLURM job submission: {e}")
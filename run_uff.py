import numpy as np
import glob
import sys
import os
from tqdm import tqdm

# Read the template for the .in file
opt = open('uff.in').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'uff/'

# Ensure the output directory exists
os.makedirs(INPDIR, exist_ok=True)

# List all .xyz files in the GEOM_DIR
xyz_files = glob.glob(os.path.join(GEOM_DIR, '*.xyz'))

for f in xyz_files:
    # Read the contents of the .xyz file, skipping the first two lines
    xyz = open(f).readlines()[2:]
    # Extract the file name without extension
    nm = os.path.basename(f).split('.')[0]
    # Combine the template, file name, and xyz contents
    ginp = opt + [nm + '\n\n'] + ['0 1\n'] + xyz + ['\n']
    # Construct the path for the output .com file
    g16 = os.path.join(INPDIR, nm + '.com')
    # Write the combined content to the .com file
    with open(g16, 'w') as com_file:
        com_file.writelines(ginp)
        
        
os.system("cp uff.sh "+INPDIR)
os.chdir(INPDIR)
os.system("sbatch uff.sh")
os.system("rm uff.sh")
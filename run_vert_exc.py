import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm


# Read the template for the .in file
opt = open('orca_vert_exc_s0.in').readlines()
sh = open('orca_vert_exc_s0.sh').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'vert_exc/'

lists = os.listdir('.')
#lists=['8']


for par in lists:
    if os.path.isdir(par) and par.isdigit():
        directory = par+'/best_geom/opt_b97-3c/'
        os.chdir(directory)
        
        # Ensure the output directory exists
        os.makedirs(INPDIR, exist_ok=True)
        
        # List all .xyz files in the GEOM_DIR
        xyz_files = glob.glob(os.path.join(GEOM_DIR, '*.xyz'))
        xyz_files = [filepath for filepath in xyz_files if '_trj' not in os.path.basename(filepath)]
        
        # Extract the alphabet and numeric parts from the filenames
        file_parts = [re.search(r"([A-Za-z]+)(\d+)", file) for file in xyz_files]
        
        # Separate the alphabets and numbers
        alphabets = [match.group(1) for match in file_parts if match]
        numbers = [int(match.group(2)) for match in file_parts if match]
        
        # Find the lowest and biggest numbers among them
        lowest_number = min(numbers)
        biggest_number = max(numbers)
        
        # Assuming you also want to find unique alphabets
        unique_alphabets = set(alphabets)
        prefix = list(unique_alphabets)[0]
        
        for f in xyz_files:
            # Read the contents of the .xyz file, skipping the first two lines
            xyz = open(f).readlines()[2:]
            # Extract the file name without extension
            nm = os.path.basename(f).split('.')[0]
            # Combine the template, file name, and xyz contents
            ginp = opt + ['* xyz 0 1'] + ['\n'] + xyz + ['*']
            # Construct the path for the output .com file
            g16 = os.path.join(INPDIR, nm + '.in')
            # Write the combined content to the .com file
            with open(g16, 'w') as com_file:
                com_file.writelines(ginp)
        
        os.chdir(INPDIR)
        
        title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_VEE\n']
        new_sh = title + sh
        open('orca_vert_exc_s0.sh', 'w').writelines(new_sh)
        
        os.system("sbatch orca_vert_exc_s0.sh")
        os.system("rm orca_vert_exc_s0.sh")
        os.chdir('../../../../')

import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm


if not os.path.isfile("orca_opt.in") or not os.path.isfile("orca_opt.sh"):
    print("Missing orca_opt.in or orca_opt.sh in the current directory.")
    sys.exit(1)


with open("orca_opt.in") as f:
    opt = f.readlines()
with open("orca_opt.sh") as f:
    sh = f.readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'opt_b97-3c/'


valid_dirs = os.listdir('.')
#omit_dirs = ['9', '10', '21', '22', '23', '29', '41', '42', '56', '63', '80']
#valid_dirs = [item for item in lists if item not in omit_lists]

#valid_dirs = ['9', '10', '21', '22', '23', '29', '41', '42', '56', '63', '80']


for par in valid_dirs:
    if os.path.isdir(par) and par.isdigit():
        directory = par+'/best_geom/'
        os.chdir(directory)
        
        # Ensure the output directory exists
        os.makedirs(INPDIR, exist_ok=True)
        
        # List all .xyz files in the GEOM_DIR
        xyz_files = glob.glob(os.path.join(GEOM_DIR, '*.xyz'))
        
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
        
        title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_GO\n']
        new_sh = title + sh
        open('orca_opt.sh', 'w').writelines(new_sh)
        
        os.system("sbatch orca_opt.sh")
        os.system("rm orca_opt.sh")
        os.chdir('../../../')

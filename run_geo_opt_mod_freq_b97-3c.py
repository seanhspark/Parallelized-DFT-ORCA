import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm



sh = open('orca_opt.sh').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'opt_b97-3c/'


valid_dirs = os.listdir('.')
#valid_dirs = [d for d in valid_dirs if '17' not in d and '19' not in d]
#valid_dirs = ['2', '13', '24', '31', '39', '49', '50', '58', '63', '68', '73', '74']

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
        
        
        os.chdir(INPDIR)
        
        title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_GO\n']
        new_sh = title + sh
        open('orca_opt.sh', 'w').writelines(new_sh)
        
        os.system("sbatch orca_opt.sh")
        os.system("rm orca_opt.sh")
        os.chdir('../../../')

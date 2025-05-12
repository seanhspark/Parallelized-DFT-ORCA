import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm



sh = open('orca_s1opt.sh').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 's1opt/'


lists = os.listdir('.')
#lists = [d for d in lists if '17' not in d and '19' not in d]
#lists = ['17']


for par in lists:
    if os.path.isdir(par) and par.isdigit():
        directory = par+'/best_geom/opt/'
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
        
        title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_S1O\n']
        new_sh = title + sh
        open('orca_s1opt.sh', 'w').writelines(new_sh)
        
        os.system("sbatch orca_s1opt.sh")
        os.system("rm orca_s1opt.sh")
        os.chdir('../../../../')
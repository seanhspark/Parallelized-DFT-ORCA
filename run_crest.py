import math
import os
import sys
import re
import random
import numpy
import time
import glob

# Read the template for the .in file
sh = open('crest.sh').readlines()

valid_dirs = os.listdir('.')
#valid_dirs = [d for d in valid_dirs if '6' not in d and '7' not in d]
#valid_dirs = ['9', '10', '21', '22', '29', '41', '56', '80']

#valid_dirs = [str(i) for i in range(41, 88)]


for par in valid_dirs:
    if os.path.isdir(par):
        os.chdir(par)
        
        # List all .xyz files in the current directory
        xyz_files = sorted(glob.glob("*.xyz"))
        
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
        
        title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_CR\n']
        new_sh = title + sh
        open('crest.sh', 'w').writelines(new_sh)
        os.system("sbatch crest.sh")
        os.system("rm crest.sh")
        os.chdir('../')

import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm


# Read the template for the .in file
if not os.path.isfile("orca_s0_freq.in") or not os.path.isfile("orca_freq.sh"):
    print("Missing orca_s0_freq.in or orca_freq.sh in the current directory.")
    sys.exit(1)

with open("orca_s0_freq.in") as f:
    opt = f.readlines()
with open("orca_freq.sh") as f:
    sh = f.readlines()

GEOM_DIR = '.'
INPDIR = 'freq/'
TMPDIR = 'tmp/' 



valid_dirs = os.listdir('.')
#omit_dirs = ['9', '10', '21', '22', '23', '29', '40', '41', '42', '56', '63', '80']
#valid_dirs = [item for item in lists if item not in omit_lists]
#valid_dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.isdigit() and os.path.exists(os.path.join(d, 'best_geom', 'opt_b97-3c'))]

for par in valid_dirs:

	directory = os.path.join(par, 'best_geom', 'opt_b97-3c')
	os.chdir(directory)

	# Ensure the output directory exists
	os.makedirs(INPDIR, exist_ok=True)
	os.makedirs(TMPDIR, exist_ok=True)

	# List all .xyz files in the GEOM_DIR
	xyz_files = glob.glob(os.path.join(GEOM_DIR, '*.xyz'))
	xyz_files = [filepath for filepath in xyz_files if '_trj' not in os.path.basename(filepath)]

	# iterate over the .xyz files to copy the .xyz files to the tmp directory
	for f in xyz_files:
		os.system(f'cp {f} {TMPDIR}')

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

	title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_0FREQ\n']
	new_sh = title + sh
	open('orca_freq.sh', 'w').writelines(new_sh)

	os.system("sbatch orca_freq.sh")
	os.system("rm orca_freq.sh")
	os.chdir('../../../../')
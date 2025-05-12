import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm


# Read the template for the .in file
opt = open('orca_s1opt.in').readlines()
sh = open('orca_s1opt.sh').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 's1opt/'

lists = os.listdir('.')
#lists = [item for item in lists if item != '1']

for par in lists:
    if os.path.isdir(par) and par.isdigit():
        directory = par+'/best_geom/opt_b97-3c/'
        os.chdir(directory)

        if not os.path.exists(INPDIR):
            
            # Ensure the output directory exists
            os.makedirs(INPDIR, exist_ok=False)
            
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
            
            title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_S1O\n']
            new_sh = title + sh
            open('orca_s1opt.sh', 'w').writelines(new_sh)
            
            os.system("sbatch orca_s1opt.sh")
            os.system("rm orca_s1opt.sh")
            os.chdir('../../../../')

        else:
            print("s1opt directory of "+par+" already exists. The previous job will be continued...\n")
            os.chdir(INPDIR)
            xyz_files = glob.glob(os.path.join(GEOM_DIR, '*.xyz'))
            xyz_files = [filepath for filepath in xyz_files if '_trj' not in os.path.basename(filepath)]
            # from xyz_files, make a list that contains './*.out' instead of './*.xyz'
            out_files = [os.path.basename(f).split('.')[0]+'.out' for f in xyz_files]
            # check each out_files if it contains "ORCA TERMINATED NORMALLY"
            if out_files:
                for f in out_files:
                    if os.path.exists(f):
                        out = open(f).readlines()
                        # Check if the ORCA TERMINATED NORMALLY is in '-2'th line in the out file
                        if 'ORCA TERMINATED NORMALLY' in out[-2]:
                            # make a list of files that contains 'f.split('.')[0]+'*.tmp'' in the current directory and delete them
                            tmp_files = glob.glob(os.path.basename(f).split('.')[0]+'*.tmp')
                            # Check if the tmp_files list is empty
                            if tmp_files:
                                print(os.path.basename(f).split('.')[0]+' is already optimized, so the temporary files are deleted.\n')
                                for tmp in tmp_files:
                                    os.system("rm "+tmp)

            for f in xyz_files:
                os.system("cp "+f+" ../tmp/")
            
            os.chdir('../tmp/')

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
                g16 = os.path.join("../"+INPDIR, nm + '.in')
                # Write the combined content to the .com file
                with open(g16, 'w') as com_file:
                    com_file.writelines(ginp)

            os.chdir("../"+INPDIR)
            
            title = ['#!/bin/bash\n#SBATCH --job-name=' + prefix + str(lowest_number) +'-'+ str(biggest_number) +'_S1O\n']
            new_sh = title + sh
            open('orca_s1opt.sh', 'w').writelines(new_sh)
            
            os.system("sbatch orca_s1opt.sh")
            os.system("rm orca_s1opt.sh")
            os.chdir('../../../../')

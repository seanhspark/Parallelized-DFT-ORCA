import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm


# Read the template for the .in file
opt = open('/home/a/aspuru/seanpark/script/nto/dens_ana.in').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'nto_mulliken'


lists = os.listdir('.')


for par in lists:
    if os.path.isdir(par) and par.isdigit():
        directory = par+'/best_geom/opt_b97-3c/vert_exc'
        os.chdir(directory)
        
        # List all .xyz files in the GEOM_DIR
        cis_files = glob.glob(os.path.join(GEOM_DIR, '*.cis'))

        for f in cis_files:
            cis = f.replace('./', '')
            tmp = f.replace('.cis', '.out')
            out_file = tmp.replace('./', '')
            tmp = f.replace('.cis', '')
            name = tmp.replace('./', '')
            os.makedirs(INPDIR, exist_ok=True)
            os.chdir(INPDIR)
            os.makedirs(name, exist_ok=True)
            os.chdir(name)
            print(os.getcwd())
            os.system("cp ../../"+cis+" .")
            os.system("mv "+f+" orca.cis")
            os.system("cp ../../"+out_file+" .")
            os.system("cp ../../"+name+".gbw .")
            ginp = ["rtype='orca'\n"] + ["rfile='"+out_file+"'\n"] + ["read_binary=True\n"] + ["mo_file='"+name+".molden.input'\n"] + opt
            # Write the combined content to the .com file
            with open('dens_ana.in', 'w') as com_file:
                com_file.writelines(ginp)
            #os.system(f"$ORCAPATH/orca_2mkl {name} -molden")
            os.chdir("../..")
        
        os.chdir("../../../..")

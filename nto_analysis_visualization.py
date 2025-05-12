import numpy as np
import glob
import sys
import os
import re
from tqdm import tqdm
from datetime import datetime

import rdkit
from rdkit import Chem
from rdkit.Chem import AllChem

import xyz2mol
"""
Make sure your dependencies
pip install numpy networkx

Then install xyz2mol:
pip install git+https://github.com/jensengroup/xyz2mol.git
"""

cap_smiles = 'CC(c1c2cccc1)(C)c3c2cccc3' # fluorene (Cap A)
#cap_smile = 'CC1(C)c2ccccc2-c2ccc(-c3ccc4c(c3)c3ccccc3n4-c3ccccc3)cc21' # Cap B

def get_indices(input_xyz, cap_smiles, log_file):
    atoms, charge, xyz_coordinates = xyz2mol.read_xyz_file(input_xyz)
    mol = xyz2mol.xyz2mol(atoms, xyz_coordinates, charge)
    mol = mol[0]

    # make SMART pattern for the fluorene
    fluorene_pattern = Chem.MolFromSmarts(cap_smiles)

    # Get the atom indices of the fluorene pattern
    fluorene_indices = mol.GetSubstructMatches(fluorene_pattern)
    fluorene_indices = [sorted(indices) for indices in fluorene_indices]

    min_max = {}
    counter = 0
    for indices in fluorene_indices:
        min_idx = min(indices)
        min_max[counter] = min_idx
        counter += 1

    # Make a list of the indices of the caps. Compare the values of the dictionary. The keys with the minimum and maximum value are the indices of the caps.
    cap_indices = [fluorene_indices[key] for key, value in min_max.items() if value == min(min_max.values()) or value == max(min_max.values())]

    # highlight the matched atoms and visualize the molecule
    highlight_atoms = [idx for indices in cap_indices for idx in indices]
    highlight_atoms = list(set(highlight_atoms))  # Remove duplicates

    if len(cap_indices) != 2:
        log_message = f"Warning: {input_xyz}: {cap_indices} There should be two CAPs in the molecule.\n"
        print(log_message)
        with open(log_file, 'a') as log:
            log.write(log_message)

    # Get the indices of the rest of heavy atoms in the molecule. Exclude hydrogens
    rest_atoms = [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetAtomicNum() != 1 and atom.GetIdx() not in highlight_atoms]

    # add '1' to the indices to start from 1
    cap_indices = [sorted(list(idx + 1 for idx in indices)) for indices in cap_indices]
    rest_atoms = [sorted(list(idx + 1 for idx in rest_atoms))]
    
    if len(rest_atoms) != 1:
        log_message = f"Warning: {input_xyz}: {rest_atoms} There should be only one CORE in the molecule.\n"
        print(log_message)
        with open(log_file, 'a') as log:
            log.write(log_message)

    indices = str(cap_indices + rest_atoms)

    return indices



# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'nto_mulliken'


lists = os.listdir('.')


current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = f"nto_parsing_log_{current_time}.txt"


for par in lists:
    if os.path.isdir(par) and par.isdigit():
        directory = par+'/best_geom/opt_b97-3c/vert_exc/'+INPDIR
        os.chdir(directory)
        
        sub_lists = os.listdir('.')

        for f in sub_lists:
            os.chdir(f)
            
            print(f"*** {f} ***")
            
            try:
                with open('dens_ana.in', 'r') as dens_ana:
                    line_check = dens_ana.readlines()
                    
                # Check if the 5th line starts with "at_lists="
                if len(line_check) >= 5 and line_check[4].startswith("at_lists=[[1,"):
                    # Continue with the next iteration or logic
                    print(f"{f} already has atom labeling.\n")
                    os.chdir('../')
                    continue
    
                if not os.path.exists('tden_summ.txt_bkb'):
                    os.system("mv tden_summ.txt tden_summ.txt_bkb")
                else:
                    print(f+" tden_summ.txt_bkb already exists.")
    
                if not os.path.exists('dens_ana.in_bkb'):
                    os.system("mv dens_ana.in dens_ana.in_bkb")
                else:
                    print(f+" dens_ana.in_bkb already exists.")
    
    
                # Read the content of the file
                with open('nto_jmol.spt', 'r') as file:
                    lines = file.readlines()
                    
    
                indices = get_indices('../../../'+f+'.xyz', cap_smiles, log_file)
                    
                ginp = (
                    ["rtype='orca'\n"] +
                    ["rfile='"+f+".out'\n"] +
                    ["read_binary=True\n"] +
                    ["mo_file='"+f+".molden.input'\n"] +
                    ["at_lists="+indices+"\n"] +
                    ["Om_formula=1\n"] + # 1: Mulliken, 2: Lowdin
                    ["eh_pop=1\n"] +
                    ["comp_ntos=True\n"] +
                    ["comp_dntos=False\n"] +
                    ["jmol_orbitals=True\n"] +
                    ["molden_orbitals=True\n"] +
                    ["alphabeta=False\n"] +
                    ["prop_list=['Om', 'POS', 'PR', 'CT', 'COH', 'CTnt', 'PRNTO', 'Z_HE']\n"]
                )
                
                # Write the new dens_ana.in file
                with open('dens_ana.in', 'w') as com_file:
                    com_file.writelines(ginp)
    
                # Modify the content
                modified_lines = []
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
    
                    # 1. Check if the line is exactly 'mo fill'
                    if line == 'mo fill':
                        # Replace 'mo fill' with 'mo fill nomesh'
                        line = 'mo fill nomesh'
                    
                    modified_lines.append(line + '\n')
    
                    # 2. Check if the line contains 'mo color'
                    if 'mo color' in line:
                        # Check if the next line does not contain 'mo translucent'
                        if i + 1 < len(lines) and 'mo translucent' not in lines[i + 1]:
                            modified_lines.append('mo translucent 0.5\n')
                    
                    i += 1
    
                # Write the modified content back to the file
                with open('nto_jmol.spt', 'w') as file:
                    file.writelines(modified_lines)
                
                print(f"{f} DONE\n")
                os.chdir("../")
                
            except:
                print("ERROR\n")
                os.chdir("../")
        
        os.chdir("../../../../..")

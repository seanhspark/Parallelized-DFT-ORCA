import os
import sys
import pandas as pd
import ast

import rdkit
from rdkit import Chem
from rdkit.Chem import AllChem

import xyz2mol
"""
This script requires xyz2mol. Install as follows:
Make sure your dependencies
pip install numpy networkx

Then install xyz2mol:
pip install git+https://github.com/jensengroup/xyz2mol.git
"""


cap_smiles = 'CC(c1c2cccc1)(C)c3c2cccc3' # fluorene (Cap A)

def get_indices(input_xyz, cap_smiles):
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

    assert len(cap_indices) == 2, f"There should be two CAPs in the molecule. {input_xyz}: {cap_indices}"

    # Get the indices of the rest of heavy atoms in the molecule. Exclude hydrogens
    rest_atoms = [atom.GetIdx() for atom in mol.GetAtoms() if atom.GetAtomicNum() != 1 and atom.GetIdx() not in highlight_atoms]

    # add '1' to the indices to start from 1
    cap_indices = [sorted(list(idx + 1 for idx in indices)) for indices in cap_indices]
    rest_atoms = [sorted(list(idx + 1 for idx in rest_atoms))]
    
    assert len(rest_atoms) == 1, f"There should be only one CORE in the molecule. {input_xyz}: {rest_atoms}"

    indices = cap_indices + rest_atoms
    indices = str([[l-1 for l in frag_l] for frag_l in indices])

    return indices


def get_dihedral_angle(xyz_file, indices, state):

    with open(xyz_file) as f:
        xyz = f.readlines()
        xyz = xyz[2:]
        xyz = [line.split() for line in xyz]

    indices = ast.literal_eval(indices)

    natoms = len(xyz)
    import numpy as np
    distance_matrix = np.zeros((natoms, natoms))
    for i in range(natoms):
        for j in range(natoms):
            distance_matrix[i, j] = np.linalg.norm(np.array(xyz[i][1:4],dtype=np.float64) - np.array(xyz[j][1:4], dtype=np.float64))

    distance_cutoff = 2.0
    nfrags = 3
    contact_atoms = []
    for ifrag in range(nfrags):
        for jfrag in range(ifrag, nfrags):
            if ifrag == jfrag:
                continue
            ij_distances = distance_matrix[indices[ifrag], :][:, indices[jfrag]]

            if np.min(ij_distances) < distance_cutoff:
                ij_contact = np.unravel_index(np.argmin(ij_distances), ij_distances.shape)
                # print(f'Frag {ifrag} and {jfrag} have {ij_contact} contacts')
                contact_atoms.append((indices[ifrag][ij_contact[0]], indices[jfrag][ij_contact[1]]))

    nneighbors = 3
    neighbors_of_contact_atoms = []
    for i, j in contact_atoms:
        i_neigh = np.argsort(distance_matrix[i])[1:nneighbors+1]
        j_neigh = np.argsort(distance_matrix[j])[1:nneighbors+1]
        i_neigh = i_neigh[i_neigh != j]
        j_neigh = j_neigh[j_neigh != i]
        neighbors_of_contact_atoms.append(((i, i_neigh), (j, j_neigh)))

    df = pd.DataFrame(
        [{
            'id': os.path.basename(xyz_file).split('.')[0],
        }]
    )

    switch = False
    counter = 1
    # calculate dihedral angle
    for i, j in neighbors_of_contact_atoms:
        i, i_neigh = i
        j, j_neigh = j
        for k in i_neigh:
            for l in j_neigh:
                if switch == False:
                    site = 'a'
                else:
                    site = 'b'

                b1 = np.array(xyz[k][1:4],dtype=np.float64) - np.array(xyz[i][1:4], dtype=np.float64)
                b2 = np.array(xyz[i][1:4],dtype=np.float64) - np.array(xyz[j][1:4], dtype=np.float64)
                b3 = np.array(xyz[j][1:4],dtype=np.float64) - np.array(xyz[l][1:4], dtype=np.float64)
                b1 /= np.linalg.norm(b1)
                b2 /= np.linalg.norm(b2)
                b3 /= np.linalg.norm(b3)
                n1 = np.cross(b1, b2)
                n2 = np.cross(b2, b3)
                n1 /= np.linalg.norm(n1)
                n2 /= np.linalg.norm(n2)
                m1 = np.cross(n1, b2)
                x = np.dot(n1, n2)
                y = np.dot(m1, n2)
                dihedral = np.arctan2(y, x)
                dihedral_angle = dihedral*180/np.pi
                if dihedral_angle <= 0 and dihedral_angle > -90:
                    dihedral_angle = abs(dihedral_angle)
                elif dihedral_angle <= -90 and dihedral_angle > -180:
                    dihedral_angle = 180 + dihedral_angle
                elif dihedral_angle > 0 and dihedral_angle <= 90:
                    dihedral_angle = dihedral_angle
                else:
                    dihedral_angle = 180 - dihedral_angle

                # Add the results to the DataFrame
                df_sub = pd.DataFrame(
                    [{
                    f'atom_idx_{site}{counter}1': k + 1,
                    f'atom_idx_{site}{counter}2': i + 1,
                    f'atom_idx_{site}{counter}3': j + 1,
                    f'atom_idx_{site}{counter}4': l + 1,
                    f'dihedral_{site}{counter}': dihedral_angle
                    }]
                )

                df = pd.concat([df, df_sub], axis=1)
                counter += 1
        switch = True
        counter = 1

    state = 0

    try:
        df_avg = pd.DataFrame(
            [{
                f's{state}_dihedral_avg_a': (df['dihedral_a1'][0] + df['dihedral_a2'][0] + df['dihedral_a3'][0] + df['dihedral_a4'][0])/4,
                f's{state}_dihedral_avg_b': (df['dihedral_b1'][0] + df['dihedral_b2'][0] + df['dihedral_b3'][0] + df['dihedral_b4'][0])/4
            }]
        )

    except:
        df_avg = pd.DataFrame(
            [{
                f's{state}_dihedral_avg_a': "ERROR",
                f's{state}_dihedral_avg_b': "ERROR"
            }]
        )

    df = pd.concat([df, df_avg], axis=1)
    df = df.loc[:,~df.columns.duplicated()]

    # df_out = pd.DataFrame(
    #     [{
    #         f's{state}_dihedral_avg_a': df['dihedral_avg_a'][0],
    #         f's{state}_dihedral_avg_b': df['dihedral_avg_b'][0]
    #     }]
    # )

    return df


# Initialize a counter
numeric_dir_count = 0

# List everything in the current directory
for item in os.listdir('.'):
    # Check if the item is a directory and has a numeric name
    if os.path.isdir(item) and item.isdigit():
        numeric_dir_count += 1
print("Total number of subdirectories: "+str(numeric_dir_count))


df_s0_void = pd.DataFrame()
df_s1_void = pd.DataFrame()

# Loop through subdirectories
for subdir in range(1, numeric_dir_count+1):  # Modify the range for your actual number of directories 
    print("Subdir "+str(subdir)+" is being processed...")

    subdir_path_opt = os.path.join(str(subdir), "best_geom/opt/")

    for filename in os.listdir(subdir_path_opt):
        if filename.startswith("slurm-") or filename.endswith("_trj.xyz"):
            continue
        elif filename.endswith(".xyz"):
            print(f"*** {filename} ***")
            if filename == "SPA209.xyz": # Manual input if needed
                indices = "[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 41, 42], [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], [14, 15, 16, 17, 33, 34, 35, 36, 37, 38, 39, 40]]"
            else:
                indices = get_indices(os.path.join(subdir_path_opt, filename), cap_smiles)

            s0 = get_dihedral_angle(os.path.join(subdir_path_opt, filename), indices, 0)

            df_s0_void = pd.concat([df_s0_void, s0], axis=0)

#    subdir_path_s1opt = os.path.join(str(subdir), "best_geom/opt/s1opt/")
    
#    for filename in os.listdir(subdir_path_s1opt):
#        if filename.startswith("slurm-") or filename.endswith("_trj.xyz"):
#            continue
#        elif filename.endswith(".xyz"):
#            if filename == "SPA209.xyz": # Manual input if needed
#                indices = "[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 41, 42], [18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32], [14, 15, 16, 17, 33, 34, 35, 36, 37, 38, 39, 40]]"
#            else:
#                indices = get_indices(os.path.join(subdir_path_s1opt, filename), cap_smiles)
            
#            s1 = get_dihedral_angle(os.path.join(subdir_path_s1opt, filename), indices, 1)

#            df_s1_void = pd.concat([df_s1_void, s1], axis=0)

# Sort rows by 'id'
df_s0_void = df_s0_void.sort_values(by='id')
#df_s1_void = df_s1_void.sort_values(by='id')

df_s0_void.to_csv("dihedral_angle_s0.csv", index=False)
#df_s1_void.to_csv("dihedral_angle_s1.csv", index=False)

print("Successfully saved.")
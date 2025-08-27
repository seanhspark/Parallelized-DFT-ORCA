import glob
import os

# Directory where parsed XYZs will go
INPDIR = 'opt_xyz/'
os.makedirs(INPDIR, exist_ok=True)

# Mapping from atomic number to element symbol
mapping = {
    '1': 'H', '2': 'He', '5': 'B', '6': 'C', '7': 'N', '8': 'O', '9': 'F',
    '14': 'Si', '16': 'S', '17': 'Cl', '22': 'Ti', '35': 'Br', '40': 'Zr',
    '53': 'I', '72': 'Hf'
}

# Collect all .out files that are not SLURM logs
out_files = [
    f for f in glob.glob('./*.out')
    if os.path.basename(f).split('.')[0].isdigit()
]

def is_gaussian_successful(filepath):
    with open(filepath) as f:
        content = f.read()
    return 'Normal termination of Gaussian 16 at' in content

# Identify valid and invalid .out files
valid_files = []
invalid_files = []

for f in out_files:
    if is_gaussian_successful(f):
        valid_files.append(f)
    else:
        invalid_files.append(f)

print(f"All : {len(out_files)}")
print(f"Valid : {len(valid_files)}")
print(f"Nonvalid : {invalid_files}")

# Save nonvalid files to a text log
with open('nonvalid_files.txt', 'w') as nf:
    for f in invalid_files:
        nf.write(f + '\n')

def extract_xyz_from_out(filepath):
    with open(filepath) as f:
        lines = f.readlines()

    lines = [line.rstrip('\n') for line in lines]
    optimized = False
    std_orientation_idx = -1

    for i, line in enumerate(lines):
        if 'Optimization completed' in line:
            optimized = True
        if optimized and 'Standard orientation:' in line:
            std_orientation_idx = i
            break

    if std_orientation_idx == -1:
        raise ValueError("No optimized structure found")

    atoms_lines = []
    for line in lines[std_orientation_idx:]:
        if 'Rotational constants (GHZ):' in line:
            break
        atoms_lines.append(line.split())

    species = []
    for row in atoms_lines[5:-1]:
        if len(row) < 6:
            continue
        atomic_number = row[1]
        symbol = mapping.get(atomic_number, atomic_number)
        x, y, z = row[3], row[4], row[5]
        species.append([symbol, x, y, z])

    xyz_name = os.path.join(INPDIR, os.path.basename(filepath).replace('.out', '.xyz'))
    with open(xyz_name, 'w') as out_xyz:
        out_xyz.write(f"{len(species)}\n\n")
        for atom in species:
            out_xyz.write('\t'.join(atom) + '\n')

# Extract optimized geometries
for f in valid_files:
    try:
        extract_xyz_from_out(f)
    except Exception as e:
        print(f"Failed to parse {f}: {e}")
        with open("parsing_errors.txt", "a") as log:
            log.write(f"{f}: {str(e)}\n")

# Remove accidentally parsed slurm logs (extra precaution)
os.system("rm -f " + os.path.join(INPDIR, "slurm-*.xyz"))
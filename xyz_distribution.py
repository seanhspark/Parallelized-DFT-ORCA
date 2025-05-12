import os
import shutil

# label = 'SPA'
n_dist = 5

# Get all files that start with 'SPA' and end with '.xyz'
xyz_files = [f for f in os.listdir('.') if f.endswith('.xyz')]
xyz_files.sort()  # Sort files by name

# Calculate the number of subdirectories needed
num_subdirs = -(-len(xyz_files) // n_dist)  # Ceiling division

# Create subdirectories and distribute files
for i in range(num_subdirs):
    subdir_name = str(i + 1)  # Subdirectory names start from '1'
    os.makedirs(subdir_name, exist_ok=True)  # Create subdirectory if it doesn't exist

    # Move up to 10 files into the current subdirectory
    for file in xyz_files[i*n_dist:(i+1)*n_dist]:
        shutil.move(file, os.path.join(subdir_name, file))

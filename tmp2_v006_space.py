import re
import os

def modify_input_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    MATCH = False

    modified_lines = []
    for line in lines:
        # Check if the line matches the pattern "* xyz 0 1C x.xxxxxx x.xxxxxx x.xxxxxx"
        match = re.match(r'(\* xyz 0 1)([A-Za-z]) (-?\d+\.\d+) (-?\d+\.\d+) (-?\d+\.\d+)', line)
        if match:
            print(f"{file_path} will be modified")
            MATCH = True
            # Extract the parts from the match
            modified_lines.append(match.group(1) + '\n')
            modified_lines.append(f"{match.group(2)} {match.group(3)} {match.group(4)} {match.group(5)}\n")
        else:
            modified_lines.append(line)

    # Write the modified lines back to the file
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)
        
    return MATCH


# Initialize a counter
numeric_dir_count = 0

# List everything in the current directory
for item in os.listdir('.'):
  # Check if the item is a directory and has a numeric name
  if os.path.isdir(item) and item.isdigit():
      numeric_dir_count += 1
print("Total number of subdirectories: "+str(numeric_dir_count))

counter = 0

for subdir in range(1, numeric_dir_count + 1):  # Modify the range for your actual number of directories 
    print("\nSubdir " + str(subdir) + " is being processed...")
    subdir_path = os.path.join(str(subdir), "best_geom", "opt")
    
    # Loop through .out files in the subdirectory
    for filename in sorted(os.listdir(subdir_path)):
        if filename.startswith("slurm-"):
            continue
        elif filename.endswith(".in"):
            MATCH = modify_input_file(os.path.join(subdir_path, filename))
            if MATCH == True:
                counter += 1

print()
print(f"{counter} files were modified")
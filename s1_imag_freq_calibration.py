import numpy as np
import glob
import os
import sys


def removing_imag(ff):
    with open(ff) as f:
        name = os.path.basename(ff).split('.')[0]
        inp_dir = os.path.join(os.path.dirname(ff), str(name+'.in'))
        parent_dir = os.path.dirname(os.path.dirname(ff))
        # vert_dir = os.path.join(parent_dir, 'vert_exc')
        # s1o_dir = os.path.join(parent_dir, 's1opt')
        freq_dir = os.path.dirname(ff)
        lines = f.readlines()
        Nimag = 0
        imags = []
        for i in range(len(lines)):
            if '***imaginary mode***' in lines[i]:
                Nimag += 1
                imags.append(lines[i].split()[1])
        
        IMAGINARY = False
        if Nimag > 0:
            IMAGINARY = True
            print(f"{name} has imaginary modes. Input file {name}.in will be modified...")
            os.system('/project/a/aspuru/orca/orca503/orca_pltvib '+ff+' 6')
            with open(ff+'.v006.xyz') as h:
                flines = h.readlines()
                natoms = int(flines[0])
                coord = []
                #ani = flines[natoms + 4 : 2* natoms + 4]
                # ani = flines[15*(natoms + 2) + 2 : 16 * (natoms + 2)]
                #ani = flines[2*(natoms + 2) + 2 : 3 * (natoms + 2)]
                #ani = flines[3*(natoms + 2) + 2 : 4 * (natoms + 2)]
                #ani = flines[8*(natoms + 2) + 2 : 9 * (natoms + 2)]
                ani = flines[4*(natoms + 2) + 2 : 5 * (natoms + 2)]
                #ani = flines[11*(natoms + 2) + 2 : 12 * (natoms + 2)]
                for line in ani:
                    total = line.split()
                    xyz = total[:4]
                    XYZ = ' '.join(xyz)
                    coord.append(XYZ+'\n')
                    
            with open('./orca_s1opt.in') as f_inp:
                inp_lines = f_inp.readlines()
                new_lines = []
                
                # Modify the first line
                first_line = inp_lines[0].replace('opt', 'opt defgrid3')
                # first_line = inp_lines[0].replace('RIJCOSX', 'NORI')
                new_lines.append(first_line)
                
                # Process the remaining lines
                for line in inp_lines[1:]:
                    new_lines.append(line)
                    if '%maxcore ' in line:
                        new_lines.append('\n')
                        new_lines.append('* xyz 0 1\n')
                        break
                        
            new_input = new_lines + coord + ['*']
            
            open(parent_dir + '/' + name + '.in', 'w').writelines(new_input)
            
            for rfile in glob.glob(parent_dir + '/' + name + '.*'):
                if rfile != parent_dir + '/' + name + '.in':
                    os.remove(rfile)
            
#            for rfile in glob.glob(vert_dir + '/' + name + '.*'):
#                try:
#                    os.remove(rfile)
#                except:
#                    continue

#            for rfile in glob.glob(s1o_dir + '/' + name + '.*'):
#                try:
#                    os.remove(rfile)
#                except:
#                    continue

            for rfile in glob.glob(freq_dir + '/' + name + '.*'):
                if rfile != freq_dir + '/' + name + '.out.v006.xyz':
                    os.remove(rfile)
                    
            return IMAGINARY


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
    # if subdir == 17:
        # continue
    print("\nSubdir " + str(subdir) + " is being processed...")
    subdir_path = os.path.join(str(subdir), "best_geom", "opt", "s1opt", "freq")
    
    # Loop through .out files in the subdirectory
    for filename in sorted(os.listdir(subdir_path)):
        if filename.startswith("slurm-"):
            continue
        elif filename.endswith(".out"):
            IMAGINARY = removing_imag(os.path.join(subdir_path, filename))
            if IMAGINARY == True:
                counter += 1

print()
print(f"{counter} files were modified")
            


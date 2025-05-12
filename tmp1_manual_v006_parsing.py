import numpy as np
import glob
import os
import sys


def removing_imag(ff):
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
            
    with open('../../../../orca_opt.in') as f_inp:
        inp_lines = f_inp.readlines()
        new_lines = []
        
        # Modify the first line
        first_line = inp_lines[0].replace('opt', 'tightopt defgrid3')
        new_lines.append(first_line)
        
        # Process the remaining lines
        for line in inp_lines[1:]:
            new_lines.append(line)
            if '%maxcore ' in line:
                new_lines.append('\n')
                new_lines.append('* xyz 0 1\n')
                break
                
    new_input = new_lines + coord + ['*']
    
    open(ff.split('.')[0] + '.in', 'w').writelines(new_input)
    


removing_imag('SPA170.out')
            


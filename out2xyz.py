import glob
import csv
import pandas as pd
import os

a = glob.glob('./*.out')

target = a

INPDIR = 'opt_xyz/'
os.makedirs(INPDIR, exist_ok=True)

def search_error(target):
        num_list = []
        nonvalid = []
        for alpha in target:
                bb = False
                with open(alpha) as f:
                        news = f.readlines()
                        news = [ii[:-1] for ii in news]
                for i,line in enumerate(news):
                        if 'Normal termination of Gaussian 16 at' in line:
                                num_list.append(str(alpha))
                                break
                if i == len(news)-1:
                        nonvalid.append(alpha)
        return num_list, nonvalid

print('All : ', len(target))
print('Valid : ', len(search_error(target)[0]))
print('Nonvalid : ', search_error(target)[1])
valid_mol = search_error(target)[0]
mapping = {'1': 'H',
 '2': 'He',
 '5': 'B',
 '6': 'C',
 '7': 'N',
 '8': 'O',
 '9': 'F',
 '14': 'Si',
 '16': 'S',
 '17': 'Cl',
 '22': 'Ti',
 '35': 'Br',
 '40': 'Zr',
 '53': 'I',
 '72': 'Hf'
}
def xyz(target):
        coord = []
        for alpha in target:
                with open(alpha) as f:
                        news = f.readlines()
                        news = [ii[:-1] for ii in news]

                atoms_lines = []
                found_opt = False
                for i, line in enumerate(news):
                        if 'Optimization completed' in line:
                                found_opt = True
                        if found_opt and 'Standard orientation:' in line:
                                standard_orientation_line = i
                                break

                for i, line in enumerate(news[standard_orientation_line:]):
                        if 'Rotational constants (GHZ):' in line:
                                break
                        atoms_lines.append(line.split())

                species = []
                ss2 = INPDIR + alpha.split('/')[-1].split('.')[0] + '.xyz'

                f = open(ss2, 'w')
                for i in atoms_lines[5:-1]:
                        if len(i) == 0:
                                break
                        symbol = mapping.get(i[1], i[1])
                        cleaned_line = [symbol] + i[3:]
                        species.append(cleaned_line)
                f.write(str(len(species))+'\n\n')
                for i in species:
                        f.write('\t'.join(i)+'\n')
                f.close()
xyz(target)
os.system("rm "+INPDIR+"slurm-*.xyz")
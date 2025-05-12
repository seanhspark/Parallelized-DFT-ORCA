import os
import re
import glob


###
print("Printed directories that have not sufficient opt_xyzs:")

lists=os.listdir('.')

num_dir = [item for item in lists if os.path.isdir(item) and re.match('^\d+$', item)]
num_dir = sorted(num_dir)

for par in num_dir:
    os.chdir(par)
    origin_xyz = glob.glob('*.xyz')
    origin_xyz = sorted(origin_xyz)
    #### Change HERE ####
    os.chdir('best_geom/opt')
    #####################
    out_files = glob.glob('*.out')
    
    ### omitting slurm- ###
    out = [filename.replace('.out', '.xyz') for filename in sorted(out_files) if 'slurm-' not in filename]
    
    if origin_xyz != out:
        difference = [item for item in origin_xyz if item not in out]
        print(par+":", difference)
        
    ## need to change as well ##
    os.chdir('../../..')
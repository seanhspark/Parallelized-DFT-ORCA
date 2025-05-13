Note that this calculations specifically works in Niagara cluster. You will need to specify the directory of ORCA, openbabel etc. in each .sh file.


First, run below to generate .xyz coordinates and do force-field calculation.

```bash
python obabel.py
python run_uff.py
```

Once the run is done, then run below to distribute in several sub-directories and quick search the conformers.

```bash
python xyz_distribution.py
python run_crest.py
```

Once all runs are done, run below to optimize the geometry at ground state.

```bash
python run_geo_opt_b97-3c.py
```

Once all runs are done, run below to calculate frequencies.

```bash
python run_s0_freq_b97-3c.py
```

Once all runs are done, check if there are imaginary frequencies.

```bash
python get_s0_freq_check.py
```

If there is imaginary frequency, the code will automatically modify the geometry and generate the input files for geometry optimization. You will need to run another round for them.
The code will print out the list of sub-directories that contain modified inputs. For example...

Modified subdirectories: ['2', '13', '24', '31', '39', '49', '50', '58', '63', '68', '73', '74']

Copy the whole list, and paste in:

run_geo_opt_mod_freq_b97-3c.py
run_s0_freq_b97-3c.py

For instance,

```
sh = open('orca_opt.sh').readlines()

# Directory where the .xyz files are located
GEOM_DIR = '.'

# Directory where the .com files will be saved
INPDIR = 'opt_b97-3c/'

# YOUR COPIED LIST HERE
lists = ['2', '13', '24', '31', '39', '49', '50', '58', '63', '68', '73', '74']
```

Then run
```bash
python run_geo_opt_mod_freq_b97-3c.py
```

Once all runs are done, run
```bash
python run_s0_freq_b97-3c.py
```

Once all runs are done, run get_s0_freq_check.py to see if there is still imaginary frequencies. If yes, repeat the procedure again.
If all frequencies are converged, run TD-DFT to calculate properties at ground state.
```bash
python run_vert_exc.py
```

Once all runs are done, parse key parameters from each output files.
```bash
python get_vert_exc_result.py
```

The final result will be saved as "VEE_b97-3c.csv"


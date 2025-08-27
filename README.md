Note that this calculations specifically works in Niagara cluster. You will need to specify the directory of ORCA (ver. 5.0.3), CREST (ver. 2.12), openbabel (ver. 3.1.1), TheoDORE (ver. 3.1.1), Jmol (ver. 16.2.1) in each .sh file.

The whole pipeline worked with Python ver. 3.10.2.

Optional step: check if the SMILES strings are valid.

```bash
python filter_smiles.py --raw_smiles smiles_raw/ --pp_smiles smiles_pp
```

Then you can generate the gen_smiles.csv using create_gen_smiles.py.

```bash
python create_gen_smiles.py --smiles smiles_pp ----smiles_gen smiles_pp/gen_smiles.csv
```



First, run below to generate .xyz coordinates and do force-field calculation.

```bash
python obabel.py
python run_uff.py
```

If running a job with multiple cpus, you can use the parallelized version of obabel.py:

```bash
python obabel_parallel.py
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

Copy the whole list, and paste in two python scripts below:

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
If all frequencies are converged, you can collect the HOMO-LUMO energies of the optimized geometries by running:

```bash
python get_geo_opt_result.py
```

Now, run TD-DFT to calculate Franck-Condon properties at ground state, based on the optimized geometries.
```bash
python run_vert_exc.py
```

Once all runs are done, parse key parameters such as oscillator stregnths, singlet and triplet energies, spin-orbit coupling etc. from each output files. The final result will be saved as "VEE_b97-3c.csv"
```bash
python get_vert_exc_result.py
```

Now, you can run the automatic natural transition orbital (NTO) calculation. Generate input files.
To run the code below, you need to install xyz2mol.

```bash
pip install numpy networkx
pip install git+https://github.com/jensengroup/xyz2mol.git
```

Then you can run the code below:

```bash
python nto_analysis_visualization.py
python nto_analysis_visualization.sh
```

Now, you will have visualized NTOs in png in opt_b97-3c/vert_exc/nto_mulliken/
You can parse the density values of each fragment using the script below:

```bash
python get_orb_density.py
```

Then the density data will be saved in orbital_density_mulliken.csv

The theoretical calculation output example of SP001 is stored in FigShare.
This customized code was used for "A self-driving lab for discovering tunable and soluble organic lasers".
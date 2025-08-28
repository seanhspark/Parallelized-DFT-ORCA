# Automated Quantum Chemical Pipeline for Organic Laser Molecules

This repository contains a customized Python-based pipeline for high-throughput quantum chemical calculations, specifically designed for execution on the **Niagara** HPC cluster.  

The workflow automates geometry optimization, vibrational frequency checks, vertical excitation energy calculations, and natural transition orbital (NTO) analysis for organic molecules.  

> ⚠️ **Note**: This pipeline is tailored for use on the **Niagara** cluster. Please ensure the following dependencies are properly installed and their paths are specified in each `.sh` script:
- **ORCA** v5.0.3  
- **CREST** v2.12  
- **OpenBabel** v3.1.1  
- **TheoDORE** v3.1.1  
- **Jmol** v16.2.1  

The pipeline was developed and tested using **Python 3.10.2**.

---

## Step-by-Step Workflow

### 1. (Optional) Validate Raw SMILES Strings
```bash
python filter_smiles.py --raw_smiles smiles_raw/ --pp_smiles smiles_pp
```

### 2. Generate Canonicalized SMILES File
```bash
python create_gen_smiles.py --smiles smiles_pp --smiles_gen smiles_pp/gen_smiles.csv
```

### 3. Generate 3D Coordinates and Perform UFF Optimization
```bash
python obabel.py
python run_uff.py
```

#### For parallelized preprocessing:
```bash
python obabel_parallel.py
```

### 4. Conformer Search with CREST
```bash
python xyz_distribution.py
python run_crest.py
```

### 5. Ground-State Geometry Optimization
```bash
python run_geo_opt_b97-3c.py
```

### 6. Frequency Calculation (B97-3c)
```bash
python run_s0_freq_b97-3c.py
```

### 7. Check for Imaginary Frequencies
```bash
python get_s0_freq_check.py
```

If any imaginary frequencies are detected, input files for re-optimization will be automatically generated. The script will print a list of affected subdirectories:

```
Modified subdirectories: ['2', '13', '24', '31', '39', '49', '50', '58', '63', '68', '73', '74']
```

Paste this list into the following two scripts:

- `run_geo_opt_mod_freq_b97-3c.py`
- `run_s0_freq_b97-3c.py`

Example:
```python
lists = ['2', '13', '24', '31', '39', '49', '50', '58', '63', '68', '73', '74']
```

Then re-run:
```bash
python run_geo_opt_mod_freq_b97-3c.py
python run_s0_freq_b97-3c.py
```

Repeat the frequency check step until no imaginary frequencies remain.

---

### 8. Extract HOMO–LUMO Energies
```bash
python get_geo_opt_result.py
```

---

### 9. TD-DFT Calculation: Franck–Condon Properties
```bash
python run_vert_exc.py
```

### 10. Extract Key Excitation Parameters
```bash
python get_vert_exc_result.py
```

The results, including oscillator strengths, singlet/triplet energies, and spin–orbit coupling, will be saved in:
```
VEE_b97-3c.csv
```

---

### 11. Natural Transition Orbital (NTO) Analysis

#### Install Dependencies:
```bash
pip install numpy networkx
pip install git+https://github.com/jensengroup/xyz2mol.git
```

#### Generate and Visualize NTOs:
```bash
python nto_analysis_visualization.py
bash nto_analysis_visualization.sh
```

The NTO figures will be saved as PNGs in:
```
opt_b97-3c/vert_exc/nto_mulliken/
```

---

### 12. Fragment Orbital Density Decomposition
```bash
python get_orb_density.py
```

Result:
```
orbital_density_mulliken.csv
```

---

## Output Example

Example theoretical output for `SP001` is available on **FigShare**.

---

## Citation

This customized pipeline was developed and used in the study:  
**"A self-driving lab for discovering tunable and soluble organic lasers"**
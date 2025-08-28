import os
import subprocess
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm


def run_obabel(row):
    smi, mol_id = row['oligomer_smiles'], row['stock_id']
    out_file = f"{mol_id}.xyz"
    command = f'obabel -:"{smi}" -O {out_file} --gen3d best'

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if not Path(out_file).exists():
        return f"{mol_id} - ERROR: File not generated"
    return None


if __name__ == "__main__":
    df = pd.read_csv("smiles.csv")

    # Get number of workers from SLURM or fallback to all CPUs
    n_workers = int(os.environ.get("SLURM_CPUS_PER_TASK", os.cpu_count()))
    print(f"Using {n_workers} workers.")

    errors = []
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = [executor.submit(run_obabel, row) for _, row in df.iterrows()]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Generating XYZ files"):
            error = future.result()
            if error:
                errors.append(error)

    with open("obabel.log", "w") as log_file:
        for err in errors:
            log_file.write(err + "\n")


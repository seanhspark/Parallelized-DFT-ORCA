import argparse
from pathlib import Path
import pandas as pd


def create_smiles_table(smiles_root: Path, output_csv: Path):
    entries = []

    # First pass to find global max count of SMILES
    max_count = 0
    smiles_files = list(smiles_root.rglob("smiles*.txt"))
    file_smiles_map = {}

    for smiles_file in smiles_files:
        with open(smiles_file, "r") as f:
            smiles_list = [line.strip() for line in f if line.strip()]
            file_smiles_map[smiles_file] = smiles_list
            max_count = max(max_count, len(smiles_list))

    pad_width = max(4, len(str(max_count)))

    # Second pass to assign IDs and store entries
    for smiles_file, smiles_list in file_smiles_map.items():
        folder_name = smiles_file.parent.name

        for i, smi in enumerate(smiles_list, start=1):
            smiles_id = f"{folder_name}_{str(i).zfill(pad_width)}"
            entries.append({"id": smiles_id, "smiles": smi})

    df = pd.DataFrame(entries)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate gen_smiles.csv from nested SMILES .txt files")
    parser.add_argument("--smiles", type=Path, required=True, help="Path to folder containing subfolders with smiles*.txt files")
    parser.add_argument("--smiles_gen", type=Path, required=True, help="Path and filename of the output .csv (e.g., ./output/gen_smiles.csv)")
    args = parser.parse_args()

    create_smiles_table(args.smiles, args.smiles_gen)


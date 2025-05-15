import os
import argparse
from pathlib import Path
from rdkit import Chem
import pandas as pd


def process_smiles(raw_root: Path, pp_root: Path):
    valid_root = pp_root / "valid_smiles"
    invalid_root = pp_root / "invalid_smiles"
    statistics = []

    for smiles_path in raw_root.rglob("smiles*.txt"):
        with open(smiles_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        valid_smiles, invalid_smiles = [], []

        for smi in lines:
            mol = Chem.MolFromSmiles(smi)
            if mol is not None:
                valid_smiles.append(smi)
            else:
                invalid_smiles.append(smi)

        rel_path = smiles_path.parent.relative_to(raw_root)

        # Create output directories
        out_valid_dir = valid_root / rel_path
        out_invalid_dir = invalid_root / rel_path
        out_valid_dir.mkdir(parents=True, exist_ok=True)
        out_invalid_dir.mkdir(parents=True, exist_ok=True)

        # Save valid SMILES
        if valid_smiles:
            with open(out_valid_dir / "smiles.txt", "w") as f:
                f.write("\n".join(valid_smiles) + "\n")

        # Save invalid SMILES
        if invalid_smiles:
            with open(out_invalid_dir / "smiles.txt", "w") as f:
                f.write("\n".join(invalid_smiles) + "\n")

        statistics.append({
            "path": str(rel_path),
            "n_valid": len(valid_smiles),
            "n_invalid": len(invalid_smiles),
        })

    pp_root.mkdir(parents=True, exist_ok=True)
    stats_df = pd.DataFrame(statistics)
    stats_df.to_csv(pp_root / "statistics.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate SMILES and organize output.")
    parser.add_argument("--raw_smiles", required=True, type=Path, help="Path to input folder with raw SMILES")
    parser.add_argument("--pp_smiles", required=True, type=Path, help="Path to output folder for processed SMILES")
    args = parser.parse_args()

    process_smiles(args.raw_smiles, args.pp_smiles)


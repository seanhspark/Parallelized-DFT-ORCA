import subprocess
import pandas as pd

# Sample DataFrame for demonstration
df = pd.read_csv('smiles.csv')

# Define the log file name
log_file_name = "obabel.log"

# Open the log file for writing
with open(log_file_name, "w") as log_file:
    for smi, mol_id in zip(df['oligomer_smiles'], df['stock_id']):
        # Define the command to run
        command = f'obabel -:"{smi}" -O {mol_id}.xyz --gen3d best'

        # Run the command
        subprocess.run(command, shell=True, capture_output=True, text=True)

        # Check if the {id}.xyz file is generated
        try:
            # Try to open the file to check if it exists
            with open(f"{mol_id}.xyz", "r") as xyz_file:
                # If the file exists and opens successfully, we assume it's generated correctly
                pass
        except FileNotFoundError:
            # If the file does not exist, log the 'id' to the log file
            log_file.write(f"{mol_id} - ERROR: File not generated\n")

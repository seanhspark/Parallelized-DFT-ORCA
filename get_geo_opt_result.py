import pandas as pd
import os

def extract_excitation_data(filename):
  """
  Extracts excitation data (energy, wavelength, oscillator strength)
  from a single ORCA .out file, including orbital energies.

  Args:
      filename: Path to the .out file.

  Returns:
      A dictionary containing extracted data.
  """
  data = {}
  start_line = None

  with open(filename, 'r') as f:
      lines = f.readlines()

      # Find the '*** OPTIMIZATION RUN DONE ***' in the file
      DONE = False
      for i in range(len(lines) - 1, -1, -1):
          if '*** OPTIMIZATION RUN DONE ***' in lines[i]:
              DONE = True
              break
          else:
              continue
        
      if DONE == False:
        print(f"*** {filename} is incomplete ***")

      # Find the start of the orbital energy table
      for i in range(len(lines) - 1, -1, -1):
          if "ORBITAL ENERGIES" in lines[i]:
              start_line = i + 3  # Skip header line
              break

      # Extract orbital energies (find last non-zero OCC before "0.00")
      if start_line is not None:
          found_last_occ = False  # Flag to track if last "2.00" or non-zero OCC found
          for i in range(start_line, len(lines)):
              occ_value = lines[i].split()[1]
              if occ_value == "2.0000":
                found_last_occ = True
              elif occ_value == "0.0000" and found_last_occ:
                no_homo, occ_homo, Eeh_homo, EeV_homo = lines[i - 1].split()
                no_lumo, occ_lumo, Eeh_lumo, EeV_lumo = lines[i].split()
                data[f"E_HOMO(eV)"] = round(float(EeV_homo), 2)
                data[f"E_LUMO(eV)"] = round(float(EeV_lumo), 2)
                break

  return data


def main():
  """
  Iterates through subdirectories, extracts data from .out files,
  and saves results to a pandas DataFrame.
  """
  
  # Initialize a counter
  numeric_dir_count = 0
  
  # List everything in the current directory
  for item in os.listdir('.'):
    # Check if the item is a directory and has a numeric name
    if os.path.isdir(item) and item.isdigit():
        numeric_dir_count += 1
  print("Total number of subdirectories: "+str(numeric_dir_count))

  data = []
  # Loop through subdirectories
  for subdir in range(1, numeric_dir_count+1):  # Modify the range for your actual number of directories 
    print("Subdir "+str(subdir)+" is being processed...")
    subdir_path = os.path.join(str(subdir), "best_geom/opt_b97-3c/")
    # Loop through .out files in the subdirectory
    for filename in os.listdir(subdir_path):
      if filename.startswith("slurm-"):
        continue
      if filename.endswith(".out"):
        prefix = filename.split(".")[0]
        data_dict = extract_excitation_data(os.path.join(subdir_path, filename))
        print(prefix, data_dict)
        data_dict["id"] = prefix
        data.append(data_dict)
  # Create DataFrame and save to CSV
  df = pd.DataFrame(data)

  # 1. Delete rows containing 'slurm-*' in any cell
  df = df[~df.apply(lambda row: row.astype(str).str.contains("slurm-*").any(), axis=1)]

  # 2. Move 'id' column to the first place
  df = df[['id'] + [col for col in df.columns if col != 'id']]
  
  # 3. Sort rows by 'id'
  df = df.sort_values(by='id')
  
  df.to_csv(f"GO_b97-3c.csv", index=False)
  print("Successfully saved.")

if __name__ == "__main__":
  main()

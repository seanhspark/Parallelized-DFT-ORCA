import pandas as pd
import os

def extract_excitation_data(filename):
  """
  Extracts excitation data (energy, wavelength, oscillator strength)
  from a single ORCA .out file.

  Args:
      filename: Path to the .out file.

  Returns:
      A dictionary containing extracted data for up to 3 excited states.
  """
  data = {}
  start_line = None  # Initialize to None

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

      # Find the table header in reverse order
      for i in range(len(lines) - 1, -1, -1):
          if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in lines[i]:
              start_line = i + 3  # Skip header lines
              break

      # Extract data for each excited state
      for i in range(3):
          if start_line is not None:  # Check if start_line was found
              try:
                state, energy, wavelength, osc, T2, TX, TY, TZ, *_ = lines[start_line + i].split()
                data[f"E_s{state}(eV)"] = round(float(energy) * 0.00012398, 2)
                data[f"wl_s{state}(nm)"] = float(wavelength)
                data[f"osc_s{state}"] = float(osc)
                data[f"t2_s{state}"] = float(T2)
                data[f"tx_s{state}"] = float(TX)
                data[f"ty_s{state}"] = float(TY)
                data[f"tz_s{state}"] = float(TZ)
              except (IndexError, ValueError):
                pass
  return data


def extract_excitation_data_void():
  data = {}

  state = 1
  data[f"E_s{state}(eV)"] = None
  data[f"wl_s{state}(nm)"] = None
  data[f"osc_s{state}"] = None
  data[f"t2_s{state}"] = None
  data[f"tx_s{state}"] = None
  data[f"ty_s{state}"] = None
  data[f"tz_s{state}"] = None

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
    subdir_path = os.path.join(str(subdir), "best_geom/opt/s1opt/")
    # Loop through .out files in the subdirectory
    for filename in os.listdir(subdir_path):
      if filename.startswith("slurm-"):
          continue
      elif filename.endswith(".out") and ('ORCA TERMINATED NORMALLY' in open(os.path.join(subdir_path, filename)).readlines()[-2]):
          prefix = filename.split(".")[0]
          data_dict = extract_excitation_data(os.path.join(subdir_path, filename))
          print(prefix, data_dict)
          data_dict["id"] = prefix
          data.append(data_dict)
      elif filename.endswith(".out") and (not 'ORCA TERMINATED NORMALLY' in open(os.path.join(subdir_path, filename)).readlines()[-2]):
          prefix = filename.split(".")[0]
          data_dict = extract_excitation_data_void()
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
  
  df.to_csv(f"S1OPT.csv", index=False)
  print("Successfully saved.")

if __name__ == "__main__":
  main()

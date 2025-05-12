import pandas as pd
import os

def extract_excitation_data(filename):
  data = {}

  with open(filename, 'r') as f:
    lines = f.readlines()
    
    for i in range(len(lines)):
        if '1(1)A' in lines[i]:
            S1 = i
        if '1(3)A' in lines[i]:
            T1 = i

    _, E_T1, _, _, _, _, _, _, _ = lines[T1].split()
    _, E_S1, f_S1, H_Cap1, E_Cap1, H_Cap2, E_Cap2, H_Core, E_Core = lines[S1].split()
    data["E_S1"] = round(float(E_S1), 3)
    data["f_S1"] = round(float(f_S1), 3)
    data["E_T1"] = round(float(E_T1), 3)
    data["H_Cap1"] = round(float(H_Cap1), 3)
    data["E_Cap1"] = round(float(E_Cap1), 3)
    data["H_Cap2"] = round(float(H_Cap2), 3)
    data["E_Cap2"] = round(float(E_Cap2), 3)
    data["H_Core"] = round(float(H_Core), 3)
    data["E_Core"] = round(float(E_Core), 3)

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
    subdir_path = os.path.join(str(subdir), "best_geom", "opt", "vert_exc", "nto_mulliken")
    filename = 'ehFrag.txt'
    for ssubdir in os.listdir(subdir_path):
        ssubdir_path = os.path.join(str(subdir_path), str(ssubdir))
        # if the filename exists in current directory:
        if os.path.exists(str(ssubdir_path) + '/' + filename):
            data_dict = extract_excitation_data(os.path.join(str(ssubdir_path), str(filename)))
            data_dict["id"] = str(ssubdir)
            data.append(data_dict)
            print(f"{ssubdir} processed")
        else:
            continue

  # Create DataFrame and save to CSV
  df = pd.DataFrame(data)

  # 1. Delete rows containing 'slurm-*' in any cell
  df = df[~df.apply(lambda row: row.astype(str).str.contains("slurm-*").any(), axis=1)]

  # 2. Move 'id' column to the first place
  df = df[['id'] + [col for col in df.columns if col != 'id']]
  
  # 3. Sort rows by 'id'
  df = df.sort_values(by='id')
  
  df.to_csv("orbital_density_mulliken.csv", index=False)
  print("Successfully saved.")

if __name__ == "__main__":
  main()

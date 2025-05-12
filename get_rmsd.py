import pandas as pd
import os
import glob
import subprocess

"""
Requires rmsd: pip install rmsd
"""


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
  
  # Initialize lists to store data
  ids = []
  rmsds = []
  
  # Loop through subdirectories
  for subdir in range(1, numeric_dir_count+1):  # Modify the range for your actual number of directories 
    print("Subdir "+str(subdir)+" is being processed...")
    geo_path = os.path.join(str(subdir), "best_geom", "opt")
    s1opt_path = os.path.join(str(subdir), "best_geom", "opt", "s1opt")
    
    xyz_geo = glob.glob(os.path.join(str(geo_path), '*.xyz'))
    xyz_geo = [filepath for filepath in xyz_geo if '_trj' not in os.path.basename(filepath)]
    
    for name in xyz_geo:
        xyz = os.path.basename(name)
        xyz_s1o = os.path.join(str(s1opt_path), str(xyz))
        if not os.path.exists(xyz_s1o):
            print(f"{xyz_s1o} does not exist")
            continue
        else:
            command = ["calculate_rmsd", name, xyz_s1o]
            result = subprocess.run(command, capture_output=True, text=True)
            rmsd_value = float(result.stdout.strip())
            
            # Store the data in the lists
            ids.append(xyz.split('.')[0])
            rmsds.append(rmsd_value)

  # Create DataFrame and save to CSV
  df = pd.DataFrame({'id': ids, 'rmsd': rmsds})

  # 1. Delete rows containing 'slurm-*' in any cell
  df = df[~df.apply(lambda row: row.astype(str).str.contains("slurm-*").any(), axis=1)]

  # 2. Move 'id' column to the first place
  df = df[['id'] + [col for col in df.columns if col != 'id']]
  
  # 3. Sort rows by 'id'
  df = df.sort_values(by='id')
  
  df.to_csv("rmsd.csv", index=False)
  print("Successfully saved.")

if __name__ == "__main__":
  main()

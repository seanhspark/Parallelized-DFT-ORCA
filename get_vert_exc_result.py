import pandas as pd
import os

def extract_excitation_data(filename, num_states=3):
    """
    Extracts excitation data (energy, wavelength, oscillator strength)
    from an ORCA .out file for multiple excited states.

    Args:
        filename (str): Path to the ORCA .out file.
        num_states (int): Number of excited states to extract (default: 3).

    Returns:
        dict: Extracted data with excitation properties for each state.
    """
    data = {}
    start_line = None  # Initialize to None
    start_line_triplet = None
  
    count = 0

    with open(filename, 'r') as f:
        lines = f.readlines()

        # Check if the calculation completed successfully
        if not any("*** ORCA-CIS/TD-DFT FINISHED WITHOUT ERROR ***" in line for line in lines):
            print(f"*** {filename} is incomplete ***")
            return data  # Return empty dictionary if calculation is incomplete

        # Find the table header in reverse order
        for i in range(len(lines) - 1, -1, -1):
            if "ABSORPTION SPECTRUM VIA TRANSITION ELECTRIC DIPOLE MOMENTS" in lines[i] and not "SPIN ORBIT CORRECTED" in lines[i] and not "SOC CORRECTED" in lines[i]:
                start_line = i + 5  # Data starts 5 lines after the header
                break

        if start_line is None:
            print(f"*** {filename}: No excitation data found ***")
            return data  # Return empty dictionary if no table is found

        # Extract data for multiple excited states
        for i in range(num_states):
            try:
                line_data = lines[start_line + i].split()
                state_num = int(line_data[0])  # Extract state number

                # Extract and store values dynamically
                data[f"E_S{state_num}(eV)"] = round(float(line_data[1]) * 0.00012398, 2)  # Convert cm-1 to eV
                data[f"wl_S{state_num}(nm)"] = float(line_data[2])
                data[f"osc_S{state_num}"] = float(line_data[3])

            except (IndexError, ValueError) as e:
                print(f"*** Error parsing state {i+1} in {filename}: {e} ***")
                break  # Stop if there is an issue with reading states
                
        for i in range(len(lines) - 1, -1, -1):
            if "TD-DFT/TDA EXCITED STATES (TRIPLETS)" in lines[i]:
                start_line_triplet = i  # Skip header lines
                break
              
        # Start scanning from the line triplet_lines[1]
        for line in lines[start_line_triplet:]:
            if line.startswith("STATE"):
                # Extract the eV value: it's the 5th item if you split
                try:
                    parts = line.split()
                    ev_index = parts.index("eV") - 1  # find the index just before "eV"
                    data[f"E_T{count+1}(eV)"] = float(parts[ev_index])
                    count += 1
                    if count == (num_states - 1):
                        break  # Stop after collecting enough
                except (ValueError, IndexError):
                    # Skip if something wrong with line format
                    continue
                  
        try:
            data["E(S1-T1)(eV)"] = round(data["E_S1(eV)"] - data["E_T1(eV)"], 2)
        except KeyError as e:
            print(f"*** Error calculating E(S1-T1): missing key {e} in {filename} ***")
      
        return data


def main():
    """
    Iterates through subdirectories, extracts data from .out files,
    and saves results to a pandas DataFrame.
    """
    # Initialize a counter for numeric directories
    numeric_dir_count = sum(1 for item in os.listdir('.') if os.path.isdir(item) and item.isdigit())
    print(f"Total number of subdirectories: {numeric_dir_count}")

    data = []

    # Loop through numeric subdirectories
    for subdir in range(1, numeric_dir_count + 1):
        print(f"Processing subdir {subdir}...")
        subdir_path = os.path.join(str(subdir), "best_geom/opt_b97-3c/vert_exc/")

        if not os.path.exists(subdir_path):
            print(f"Warning: {subdir_path} does not exist, skipping...")
            continue

        # Loop through .out files in the subdirectory
        for filename in os.listdir(subdir_path):
            if filename.endswith(".out") and not filename.startswith("slurm-"):
                prefix = filename.split(".")[0]
                file_path = os.path.join(subdir_path, filename)

                data_dict = extract_excitation_data(file_path, num_states=3)  # Extract multiple states
                if data_dict:  # Only add if data was extracted
                    data_dict["id"] = prefix
                    data.append(data_dict)

    # Create DataFrame
    df = pd.DataFrame(data)

    if df.empty:
        print("No valid excitation data found. No CSV will be saved.")
        return

    # Move 'id' column to the first place
    df = df[['id'] + [col for col in df.columns if col != 'id']]

    # Sort rows by 'id'
    df = df.sort_values(by='id')

    # Save to CSV
    df.to_csv("VEE_b97-3c.csv", index=False)
    print("Successfully saved.")

if __name__ == "__main__":
    main()

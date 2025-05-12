import pandas as pd
import os
import re
import logging
from datetime import datetime

def extract_frequency_data(filename):
    start_line = None  # Initialize to None

    with open(filename, 'r') as f:
        lines = f.readlines()
        id = os.path.basename(filename).split('.')[0]

        # Find the '*** OPTIMIZATION RUN DONE ***' in the file
        DONE = False
        for i in range(len(lines) - 1, -1, -1):
            if '****ORCA TERMINATED NORMALLY****' in lines[i]:
                DONE = True
                break
    
        if not DONE:
            logging.info(f"*** {id} is incomplete ***")

        start_line = None
        for i in range(len(lines) - 1, -1, -1):
            if 'VIBRATIONAL FREQUENCIES' in lines[i]:
                start_line = i
                break

        if start_line is None and not DONE:
            logging.info(f"'VIBRATIONAL FREQUENCIES' not found in {id}")
            return False

        FOUND = False
        if '***imaginary mode***' in lines[start_line+11]:
            FOUND = True
            pattern = re.compile(r'(-?\d+\.\d+ cm\*\*-1)')
            match = pattern.search(lines[start_line+11])
            if match:
                extracted_value = match.group(1)
                logging.info(f"Imaginary frequency of {extracted_value} was found in {id}")

        return FOUND


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
    logging.info("Total number of subdirectories: " + str(numeric_dir_count))
  
    # Loop through subdirectories
    count_total = 0
    count_true = 0
    
    for subdir in range(1, numeric_dir_count + 1):  # Modify the range for your actual number of directories 
        count_subdir = 0
        logging.info("\nSubdir " + str(subdir) + " is being processed...")
        subdir_path = os.path.join(str(subdir), "best_geom", "opt", "s1opt", "freq")
        # Loop through .out files in the subdirectory
        for filename in sorted(os.listdir(subdir_path)):
            if filename.startswith("slurm-"):
                continue
            elif filename.endswith(".out"):
                count_total += 1
                count_subdir += 1
                if extract_frequency_data(os.path.join(subdir_path, filename)):
                    count_true += 1
                    
        if count_subdir != 10:
            logging.info(f"subdirectory {subdir} does not have '10' output files.")

    return count_total, count_true


if __name__ == "__main__":
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"s1_freq_check_log_{current_time}.txt"
    # Configure logging to write to both the console and a log file
    logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[
        logging.FileHandler(log_filename, mode='w'),
        logging.StreamHandler()
    ])

    count_total, count_true = main()
    
    logging.info("\nTotal number of files processed: " + str(count_total))
    logging.info("Number of files with imaginary frequencies: " + str(count_true))
    logging.info("\nDONE")
#!/usr/bin/python3
# Script to merge parquet output files from multiple Corsika8 runs

import pandas as pd
import os
import sys


# Directory with simulation outputs
sim_name = sys.argv[1]
output_dir = "output/" + sim_name

# Make a directory for merged outputs
os.makedirs(output_dir + "/merged", exist_ok=True)

print ("Simulation output: '", output_dir, "'", sep="")

# Map directories and output files inside
output_types = {"energyloss": "dEdX",
                "interactions": "interactions",
                "particles": "particles",
                "production_profile": "profile",
                "profile": "profile"}

# Declare dictionaries to hold dataframes
data = {}
for dir in output_types.keys():
    data[dir] = {}

# Current shower id, used for shifting shower indices
id_shw = 0

# List of subdirectories
dir_list = os.listdir(output_dir)
# Filter only run directories
for dir in dir_list:
    if "run" not in dir:
        dir_list.remove(dir)

# Number of run subdirectories
n_dirs = len(dir_list)

# Iterate over runs in this simulation
for run in range(n_dirs):
    print("Processing run", run)
    
    # Open summary file to read number of showers
    with open(output_dir + "/run_" + str(run) + "/summary.yaml", "r") as file:
        first_line = file.readline()
        n_shw = int(first_line.split()[1])
        print("  - showers = ", n_shw)

    # Shift shower index
    id_shw += n_shw
    # But not for the first run
    if (run == 0): id_shw = 0

    # Iterate over output directories and files
    for dir, file in output_types.items():
        print("  - processing output dir '", dir, "' (file '", file, ".parquet')", sep="")

        # Compose output file name
        output_file = output_dir + "/run_" + str(run) + "/" + dir + "/" + file + ".parquet"

        # Read from parquet file as dataframe
        data[dir][run] = pd.read_parquet(output_file, "pyarrow")

        # Shift shower indices
        data[dir][run]["shower"] = data[dir][run]["shower"] + id_shw

# Iterate over outputs to make merged files
for dir, file in output_types.items():
    # Make a directory for the merged output
    os.makedirs(output_dir + "/merged/" + dir, exist_ok=True)
    
    # Merge dataframes from all runs
    df_merge = pd.concat(data[dir])

    # Write merged dataframe to a parquet file
    df_merge.to_parquet(output_dir + "/merged/" + dir + "/" + file + ".parquet")

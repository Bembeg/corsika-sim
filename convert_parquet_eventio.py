import os
import sys
import numpy as np

import eventio


path_input = sys.argv[1]

print(f"Input path: {path_input}")

# paths to parquet and config files
file_parquet = path_input + "/cherenkov/light.parquet"
file_config = path_input + "/cherenkov/config.yaml"

# check files exist
if not (os.path.exists(file_parquet) or os.path.exists(file_config)):
    print("Missing input files (parquet or config)")
    


# script to convert CORSIKA 8 simulation files containing Cherenkov photon
# information (i.e. input) to the PyEventIO format (i.e. output)

import os
import sys
import yaml
import numpy as np
import pandas as pd

import eventio

import corsikaio

def print_help():
    print("Usage: python3 convert_parquet_eventio.py input [output]")
    print("       input path must contain the cherenkov subdirectory")

def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)

    if (c==1):
        return np.identity(3)

    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

version = np.float32(8.0)

# check that path to C8 output was provided
if len(sys.argv) == 1:
    print("No CORSIKA 8 output provided")
    print_help()
    sys.exit(1)

# path to input
path_input = sys.argv[1]
print(f"Input path  : '{path_input}'")

# path to output
if len(sys.argv) >= 3:
    # output name provided by user
    path_output = sys.argv[2]
else:
    # determine output name from the input
    path_input_split = path_input.strip("/").split("/")
    path_output = path_input_split[-1]
print(f"Output path : '{path_output}'")

# paths to parquet and config files
file_parquet = path_input + "/cherenkov/light.parquet"
file_config = path_input + "/cherenkov/config.yaml"

# check whether input files exist
if not (os.path.exists(file_parquet) or os.path.exists(file_config)):
    print("Missing Cherenkov files (parquet or config) in input path")
    sys.exit(2)

# define data type of the structured array for photon bunches
dtype_bunch = np.dtype([("x", np.float32),
                        ("y", np.float32),
                        ("cx", np.float32),
                        ("cy", np.float32),
                        ("time", np.float32),
                        ("zem", np.float32),
                        ("photons", np.float32),
                        ("wavelength", np.float32)])

# load input data file
data = pd.read_parquet(file_parquet, "pyarrow")

# load input config file
with open(file_config, "r") as read_file:
    conf = yaml.safe_load(read_file)

# print(conf)

# run header
print(corsikaio.subblocks.run_header.run_header_fields)
run_header_dtype_luleo = corsikaio.subblocks.run_header.get_run_header_dtype(version)

print(run_header_dtype_luleo)
observer_idx = 0

run_header = ["header", 0, 0, 8, 1, np.zeros(10), 0, 10, 10, -1, -1, 0, 0, 0, 0, np.zeros(50), 0, 0, 0, 0, 0, 0, 0, 1, np.zeros(40), np.zeros(5), np.zeros(11), 0, 0, np.zeros(5), np.zeros(5), np.zeros(5), 0, 0, 0, 0]
run_header = [0]*273
# print(run_header)
run_hr_array = np.array(run_header, dtype=run_header_dtype_luleo)

print(run_hr_array)

with open('test.npy', 'wb') as f:
    np.save(f, run_hr_array)

# process photon data
for observer_name in conf["observers"]:
    print(f"Processing data for telescope '{observer_name}'")

    center = conf["observers"][observer_name]["position"]
    pointing = conf["observers"][observer_name]["pointing"]
    radius = conf["observers"][observer_name]["radius"]
    
    # filter dataframe for this observer only
    filtered_data = data[data["obsId"] == observer_idx]
    
    # calculate rotation matrix to transform points onto the ground plane
    rotation_matrix = rotation_matrix_from_vectors(pointing, [0, 0, 1])

    # hits in the global coordinate system
    hits = [filtered_data["hitX"] - center[0], filtered_data["hitY"] - center[1], filtered_data["hitZ"] - center[2]]
    # transform hits to observer local coordinate system
    trf_hits = np.dot(rotation_matrix, hits)

    # hit positions in cm
    x = trf_hits[0] * 1e2
    y = trf_hits[1] * 1e2

    # hit directions in the global coordinate system
    directions = [filtered_data["dirX"], filtered_data["dirY"], filtered_data["dirZ"]]
    # transform directiosn to observer local coordinate system
    trf_directions = np.dot(rotation_matrix, directions)
    
    # calculate norms of direction vectors (should be unity, but making sure)
    direction_norms = np.sqrt(trf_directions[0] * trf_directions[0] + trf_directions[1] * trf_directions[1] + trf_directions[2] * trf_directions[2])

    # direction cosines
    cx = trf_directions[0] / direction_norms
    cy = trf_directions[1] / direction_norms

    # arrival time
    time = filtered_data["time"]

    # emission altitude in cm
    zem = filtered_data["emissionAlt"] * 1e2

    # number of photons in the bunch
    photons = filtered_data["weight"]

    # wavelength
    wavelength = filtered_data["wavelength"]

    # check lengths of all data arrays
    print("  data array lengths:")
    print(f"            x : {len(x)}")
    print(f"            y : {len(y)}")
    print(f"           cx : {len(cx)}")
    print(f"           cy : {len(cy)}")
    print(f"         time : {len(time)}")
    print(f"          zem : {len(zem)}")
    print(f"      photons : {len(photons)}")
    print(f"   wavelength : {len(wavelength)}")

    observer_idx += 1

    bunches = []
    for i in range(len(x)):
        bunch = (x[i], y[i], cx[i], cy[i], time[i], zem[i], photons[i], wavelength[i])
        bunches.append(bunch)

    bunches_array = np.array(bunches, dtype=dtype_bunch)





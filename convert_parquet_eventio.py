# script to convert CORSIKA 8 simulation files containing Cherenkov photon
# information (i.e. input) to the EventIO format (i.e. output)

import os
import sys
import yaml
import math
import random
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from pandarallel import pandarallel

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

def generate_run_header(version):
    if debug:
        print("Generating run header")

    # run header - 273 floats
    run_header = np.zeros(273).astype(np.float32) 

    # load input files
    with open(path_input + "/particles/config.yaml", "r") as file_particles:
        content_particles = yaml.safe_load(file_particles)
    with open(path_input + "/primary/summary.yaml", "r") as file_primary:
        content_primary = yaml.safe_load(file_primary)

    # observation level stored in m, convert to cm
    header_obs_level = np.float32(np.linalg.norm(content_particles["plane"]["center"]) * 1e2) 

    energies_primary = [content_primary[shower]["total_energy"] for shower in content_primary]
    header_ene_min = min(energies_primary)
    header_ene_max = max(energies_primary)
    header_n_show = len(content_primary)

    # manually define some values for the run header
    header_version = np.float32(version)
    header_n_obs_levels = np.float32(1)
  
    # put values into the run header - for reference, see run_header_fields object in corsikaio/subblocks/run_header.py
    run_header[3] = header_version
    run_header[4] = header_n_obs_levels
    run_header[5] = header_obs_level
    run_header[16] = header_ene_min
    run_header[17] = header_ene_max
    run_header[92] = header_n_show

    if (debug):
        print(f"   version    : {header_version}")
        print(f"   obs. level : {header_obs_level} cm")
        print(f"   energy min : {header_ene_min}")
        print(f"   energy max : {header_ene_max}")
        print(f"   showers    : {header_n_show}")

    # convert header to bytearray
    run_header_bytes = bytearray(run_header)

    # modify bytearray to start with the RUNH mark
    run_header_bytes[0:4] = b"RUNH"

    return run_header_bytes

def generate_event_header(version):
    if debug:
        print(f"Generating event header")

    # event header - 273 floats
    event_header = np.zeros(273).astype(np.float32)

    # mapping of primary particle IDs from CORSIKA 8 to CORSIKA 7 
    pid_map = {"Photon": 1, "Proton": 14}

    # array of first interaction altitudes
    first_ints = []
 
    # default observation altitude set to sea level
    obs_alt = 0

    # load input files
    with open(path_input + "/particles/config.yaml", "r") as file_particles:
        content_particles = yaml.safe_load(file_particles)
    with open(path_input + "/config.yaml", "r") as file_config:
        content_config = yaml.safe_load(file_config)
    with open(path_input + "/primary/summary.yaml", "r") as prim_sum:
        content_prim_sum = yaml.safe_load(prim_sum)
    with open(path_input + "/interactions/summary.yaml", "r") as int_sum:
        content_int_sum = yaml.safe_load(int_sum)
    with open(path_input + "/cherenkov/config.yaml", "r") as cher_sum:
        content_cher_sum = yaml.safe_load(cher_sum)

    # azimuth and zenith angles - initialize to 0
    ang_zen = np.float32(0)
    ang_azi = np.float32(0)

    # observation height stored in m, convert to cm
    header_obs_level = np.float32(np.linalg.norm(content_particles["plane"]["center"]) * 1e2)

    # in principle, we do not know the height of ground level, so
    # conversion between observation altitude and height is undefined

    # parse config to get the observation altitude
    args_split = content_config["args"].split()
    for arg in range(len(args_split)):
        if "observation-level" in args_split[arg]:
            # observation altitude in m
            obs_alt = np.float32(args_split[arg+1])   
        if (args_split[arg] == "-z" or args_split[arg] == "--zenith"):
            ang_zen = np.float32(math.radians(float(args_split[arg+1])))

        if (args_split[arg] == "-a" or args_split[arg] == "--azimuth"):
            ang_azi = np.float32(math.radians(float(args_split[arg+1])))

    # number of events / showers
    n_events = len(content_prim_sum)

    # primary energy and type
    header_total_energy = np.float32(content_prim_sum["shower_0"]["total_energy"])
    header_pid = np.float32(pid_map[content_prim_sum["shower_0"]["name"]])    

    # primary particle position - constant across events
    prim_x = content_prim_sum["shower_0"]["x"]
    prim_y = content_prim_sum["shower_0"]["y"]
    prim_z = content_prim_sum["shower_0"]["z"]
  
    # primary particle injection altitude in m
    header_start_height = np.linalg.norm(np.add(content_particles["plane"]["center"], [prim_x, prim_y, prim_z])) - np.linalg.norm(content_particles["plane"]["center"]) + obs_alt
    # convert to cm
    header_start_height *= 1e2

    # primary particle momentum    
    header_mom_x = content_int_sum["shower_0"]["px"]
    header_mom_y = content_int_sum["shower_0"]["py"]
    header_mom_mz = content_int_sum["shower_0"]["pz"]

    # iterate over showers to collect first interaction altitudes
    for ev_id in range(n_events):
        first_int = [content_int_sum["shower_" + str(ev_id)]["x"], content_int_sum["shower_" + str(ev_id)]["y"], content_int_sum["shower_" + str(ev_id)]["z"]]

        # first interaction height
        first_int_height = np.float32(np.linalg.norm(np.add(content_particles["plane"]["center"], first_int)))
        # convert to a.s.l. altitude
        first_int_alt = first_int_height - np.linalg.norm(content_particles["plane"]["center"]) + obs_alt 

        # first interaction altitude stored in m, convert to cm and make negative (for some reason C7 stores the number as negative, so align with it)
        first_ints.append(-first_int_alt * 1e2)

    # manually define values for the event header
    header_version = np.float32(version)
    header_n_obs_levels = np.float32(1)
    header_cher_bunch = np.float32(content_cher_sum["bunching"])
    header_cher_wavelen_min = np.float32(content_cher_sum["wavelength_min"])
    header_cher_wavelen_max = np.float32(content_cher_sum["wavelength_max"])

    # put values into the event header - for reference, see event_header_fields object in corsikaio/subblocks/event_header.py
    event_header[2] = header_pid
    event_header[3] = header_total_energy
    event_header[7] = header_mom_x
    event_header[8] = header_mom_y
    event_header[9] = -header_mom_mz    # header stores the momentum z-component with a minus
    event_header[10] = ang_zen
    event_header[11] = ang_azi
    event_header[45] = header_version
    event_header[46] = header_n_obs_levels
    event_header[47] = header_obs_level
    event_header[58] = header_total_energy
    event_header[59] = header_total_energy
    event_header[84] = header_cher_bunch
    event_header[95] = header_cher_wavelen_min
    event_header[96] = header_cher_wavelen_max
    event_header[157] = header_start_height

    # convert header to bytearray
    event_header_bytes = bytearray(event_header)
    # modify bytearray to start with the EVTH mark
    event_header_bytes[0:4] = b"EVTH"

    if (debug):
        print(f"   PID            : {header_pid}")
        print(f"   total energy   : {header_total_energy} GeV")
        print(f"   mom x          : {header_mom_x} GeV/c")
        print(f"   mom y          : {header_mom_y} GeV/c")
        print(f"   -mom z         : {-header_mom_mz} GeV/c")
        print(f"   azimuth        : {ang_azi} rad")
        print(f"   zenith         : {ang_zen} rad")
        print(f"   obs. level     : {header_obs_level} cm")
        print(f"   start height   : {header_start_height} cm")
        print(f"   1st int.       : {first_ints[-1]} cm")
        print(f"   cher. bunch    : {header_cher_bunch}")
        print(f"   cher. range    : {header_cher_wavelen_min} - {header_cher_wavelen_max} nm")

    return event_header_bytes, first_ints

def generate_telescope_definitions():
    if debug:
        print(f"Generating telescope definitions")

    # telescope definions are formatted as [position, pointing, radius] - [[x,y,z], [pX,pY,pZ], r]
    telescope_defs = []
    # rotation matrices to transform hit positions onto the ground plane
    rotation_matrices = []

    # load input files
    with open(path_input + "/cherenkov/config.yaml", "r") as read_file:
        content_cherenkov = yaml.safe_load(read_file)
    with open(path_input + "/particles/config.yaml", "r") as file_particles:
        content_particles = yaml.safe_load(file_particles)
                    
    # observation height in cm
    obs_height = np.linalg.norm(content_particles["plane"]["center"]) * 1e2

    # get telescope names
    names_tele = [tele for tele in content_cherenkov["observers"]]

    for tele in names_tele:
        # empty telescope definition
        telescope_def = []

        # get telescope position in cm
        telescope_def.append(np.multiply(content_cherenkov["observers"][tele]["position"], 1e2))
        # subtract observation level
        telescope_def[-1][2] -= obs_height
        # get pointing direction
        telescope_def.append(content_cherenkov["observers"][tele]["pointing"])
        # and radius in cm
        telescope_def.append(np.multiply(content_cherenkov["observers"][tele]["radius"], 1e2))

        # append telescope definition to the list
        telescope_defs.append(telescope_def)

        # calculate rotation matrix
        rotation_matrices.append(rotation_matrix_from_vectors(content_cherenkov["observers"][tele]["pointing"], [0, 0, 1]))

    if debug:
        tele_id = 0
        for tele in telescope_defs:
            print(f"   [{tele_id}] x = {tele[0][0]}, y = {tele[0][1]}, z = {tele[0][2]} cm")
            print(f"   [{tele_id}] px = {tele[1][0]}, py = {tele[1][1]}, pz = {tele[1][2]}")
            print(f"   [{tele_id}] r = {tele[2]} cm")     

    return telescope_defs, rotation_matrices

def generate_array_offsets():
    if debug:
        print("Generating array offsets")

    # array offsets are defined as [t,x,y]
    array_offsets = []

    # load input file
    with open(path_input + "/primary/summary.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)

    # primary particle type
    particle = content["shower_0"]["name"]    

    # primary particle position
    prim_x = content["shower_0"]["x"]
    prim_y = content["shower_0"]["y"]
    prim_z = content["shower_0"]["z"]

    # distance to observation plane center
    dist_to_obs = np.linalg.norm([prim_x, prim_y, prim_z])

    # calculate particle beta factor
    if particle == "Photon":
        beta = 1
    if particle == "Proton":
        mass = 0.93827208
        gamma = content["shower_0"]["total_energy"] / mass
        beta = np.sqrt(1 - 1 / (gamma * gamma))

    # time to observation plane center
    time_to_obs = dist_to_obs / (0.299792458 * beta)

    # only one array from CORSIKA 8
    array_offsets.append([time_to_obs, 0, 0])

    if(debug):
        for array in range(len(array_offsets)):
            print(f"   [{array}] t = {array_offsets[array][0]}, x = {array_offsets[array][1]}, y = {array_offsets[array][2]}")

    return array_offsets

def generate_input_card(version):
    if debug:
        print("Generating input card")

    # input card array, append the first line manually
    input_card = []
    input_card.append(f"CORSIKA 8 ({version}) inputs:")

    # get CLI arguments passed to a CORSIKA 8 run
    with open(path_input + "/config.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)

    # split argument string by spaces
    args_split = content["args"].split()

    # iterate over argument string
    for i in range(len(args_split)):
        if args_split[i][0] == "-":
            
            # remove trailing "-"
            arg_line = args_split[i].strip("-")

            # check that next one is not a argument key
            if args_split[i+1][0] != "-":
                # get the argument value
                arg_line += (" " + args_split[i+1])
                
            # add argument key-value pair to the input card
            input_card.append(arg_line)

    # convert input card to eventIO strings and to a bytearray
    # empty bytearray to start with
    input_card_bytes = bytearray()
    for line in input_card:
        if debug:
            print(f"   {line}")

        # eventIO string format is a 2-byte integer for length + the string itself
        input_card_bytes += np.int16(len(line)).tobytes()
        input_card_bytes += line.encode()

    return input_card_bytes, len(input_card)

def generate_event_end():
    # event end - 273 floats
    event_end_bytes = bytearray(np.zeros(273).astype(np.float32))

    # modify bytearray to start with the EVTE mark
    event_end_bytes[0:4] = b"EVTE"

    return event_end_bytes

def generate_run_end():
    # run end - 3 floats
    run_end_bytes = bytearray(np.zeros(3).astype(np.float32)) 

    # modify bytearray to start with the RUNE mark
    run_end_bytes[0:4] = b"RUNE"

    return run_end_bytes

def get_number_of_showers():
    with open(path_input + "/summary.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
    return int(content["showers"])

def generate_bytearray(row):
    # telescope/observer ID
    tele_id = np.uint32(row["obsId"])

    # form hit and direction vectors
    # subtract telescope center position from each hit position
    hitVec = np.array(np.subtract((row["hitX"], row["hitY"], row["hitZ"]), telescope_defs[tele_id][0]))
    dirVec = np.array((row["dirX"], row["dirY"], row["dirZ"]))

    # transformed hit positions (in cm) and hit directions (direction cosines) by applying the rotation matrix
    hitVecTrf = np.dot(rotation_matrices[tele_id], hitVec) * 1e2
    dirVecTrf = np.dot(rotation_matrices[tele_id], dirVec)

    # subtract array offset from photon impact times
    time = row["time"] - array_offsets[0][0]

    # convert emission altitude to cm
    emissionAlt = row["emissionAlt"] * 1e2

    # number of photons in a bunch and wavelength, unmodified
    photons = row["weight"]
    wavelength = row["wavelength"]

    # generate the float32 bytearray
    bunch_bytes = bytearray(np.array((hitVecTrf[0], hitVecTrf[1], dirVecTrf[0], dirVecTrf[1], time, emissionAlt, photons, wavelength), dtype=np.float32))

    return {"shower": row["shower"], "obsId": tele_id, "x": hitVecTrf[0], "y": hitVecTrf[1],
     "cx": dirVecTrf[0], "cy": dirVecTrf[1], "time": time, "zem": emissionAlt,
     "photons": photons, "wavelength": wavelength, "bytearray": bunch_bytes}

print("[Parquet-EventIO convertor for CORSIKA 8]")

# --- start of input ---

# debug mode
debug = False

# test conversion of bunches
test = True
# number of randomly selected bunches to test
n_tests = 1000

# parallel pandas processing using pandarallel
parallel = True

# number of workers for parallel processing (<=0 for unlimited)
n_workers = 0

# override the CORSIKA version to 8.0
version_override = 8.0

# chunk size in MB for loading the input data
chunk_size_MB = 10

# print progress every 10 events (normally too verbose)
verbose_event_print = True

# --- end of input ---

# check that path to C8 output was provided
if len(sys.argv) == 1:
    print("No CORSIKA 8 output provided")
    print_help()
    sys.exit(1)

# path to input
path_input = sys.argv[1]
print(f"   Input path  : '{path_input}'")

# default output file name - used by CORSIKA 7
default_output_name = "output.corsika"

# path to output
if len(sys.argv) >= 3:
    # output name provided by user
    path_output = sys.argv[2]
else:
    # store output in the input dir
    path_output = sys.argv[1] + "/" + default_output_name

print(f"   Output path : '{path_output}'")

# paths to cherenkov parquet and config files
path_cher_parquet = path_input + "/cherenkov/light.parquet"
path_cher_conf = path_input + "/cherenkov/config.yaml"

# check whether input files exist
if not (os.path.exists(path_cher_parquet) or os.path.exists(path_cher_conf)):
    print("   Missing Cherenkov files (parquet or config) in input path")
    sys.exit(2)

if (parallel):
    # initialize pandarallel (parallel pandas processing)
    print("Parallel processing of Pandas DataFrames enabled (using Pandarallel)")
    if (n_workers <= 0):
        pandarallel.initialize()
    else:
        pandarallel.initialize(nb_workers=n_workers)

# load input data file
cher_file = pq.ParquetFile(path_cher_parquet)

# load input cherenkov config file
with open(path_cher_conf, "r") as read_file:
    conf_cherenkov = yaml.safe_load(read_file)
    # get bunching factor
    photon_bunching = conf_cherenkov["bunching"]

# size of photon bunch (elements in the data array)
bunch_size = 8

# CORSIKA 8 photon bunch dtype size in bytes
c8_bunch_size = 92

# chunk size for loading the input data
chunk_size = int(chunk_size_MB * 1e6 / 92)

# eventIO sync marker to place before every eventIO top-level object (listed below)
sync_marker = eventio.constants.SYNC_MARKER_LITTLE_ENDIAN

# eventIO top-level object types
type_run_header = eventio.iact.RunHeader.eventio_type          # 1200
type_input_card = eventio.iact.InputCard.eventio_type          # 1212
type_tele_def = eventio.iact.TelescopeDefinition.eventio_type  # 1201
type_event_header = eventio.iact.EventHeader.eventio_type      # 1202
type_array_offsets = eventio.iact.ArrayOffsets.eventio_type    # 1203
type_tele_data = eventio.iact.TelescopeData.eventio_type       # 1204
type_event_end = eventio.iact.EventEnd.eventio_type            # 1209
type_run_end = eventio.iact.RunEnd.eventio_type                # 1210
# non top-level object types (no sync marker prefix)
type_bunch = eventio.iact.Photons.eventio_type                 # 1205

# standard word size in bytes
word_size = 4

# standard header size in EventIO objects
header_size = corsikaio.constants.BLOCK_SIZE_FLOATS
header_size_m = (header_size + 1) * word_size

# ID word serves as an additional object identifier, ignore and always set to 0
id_word = 0

print("Generating headers and EventIO metadata")

# generate the run header, (TODO disable) override version to 8.0
run_header_bytes = generate_run_header(version=version_override)

# generate the event header, (TODO disable) override version to 8.0
event_header_bytes, first_ints = generate_event_header(version=version_override)

# generate telescope definition object
telescope_defs, rotation_matrices = generate_telescope_definitions()

# generate array offsets
array_offsets = generate_array_offsets()

# generate input card, (TODO disable) override version to 8.0
input_card_bytes, input_card_lines = generate_input_card(version=version_override)

# generate event end
event_end_bytes = generate_event_end()

# generate run end
run_end_bytes = generate_run_end()

# number of events (showers)
n_events = get_number_of_showers()

# printing progress
event_print_number = 5 if n_events < 40 else int(n_events / 40)

if verbose_event_print:
    event_print_number = 10

if test:
    print(f"Conversion testing enabled: randomly selecting {n_tests} photon bunches to verify after conversion")

    # array to store [eventID, teleID, bunchID] arrays
    test_bunches = []

    # randomly select photon bunches to test
    for i in range(n_tests):
        # random event ID
        ev_id = random.randrange(0, n_events)

        # random telescope ID in that event
        tele_id = random.randrange(0, len(telescope_defs))

        # bunch ID will be chosen during the processing of a given event

        # add to test list
        test_bunches.append([ev_id, tele_id, 0])
    
    # sort by event ID
    test_bunches.sort(key=lambda x: x[0])

    # arrays to hold the reference and converted bunches
    bunches_reference = []
    bunches_converted = []

print("Writing EventIO file")
with open(path_output, 'wb') as f:
    # RUN HEADER
    f.write(sync_marker)  # sync marker
    f.write(np.int32(type_run_header).tobytes())  # type/version word
    f.write(np.int32(id_word).tobytes())  # ID word
    f.write(np.int32(header_size_m).tobytes())  # length word
    f.write(np.int32(header_size).tobytes())  # number of floats in header
    f.write(run_header_bytes)  # write run header data

    # INPUT CARD
    f.write(sync_marker)  # sync marker
    f.write(np.int32(type_input_card).tobytes())  # type/version word
    f.write(np.int32(id_word).tobytes())  # ID word
    f.write(np.int32(len(input_card_bytes) + 4).tobytes())  # length word - number of bytes in memory, extended by one 4-byte word
    f.write(np.int32(input_card_lines).tobytes())  # number of lines in input card
    f.write(input_card_bytes)  # write input card data

    # TELESCOPE DEFINITIONS
    f.write(sync_marker)  # sync marker
    f.write(np.int32(type_tele_def).tobytes())  # type/version word
    f.write(np.int32(id_word).tobytes())  # ID word
    f.write(np.int32(len(telescope_defs) * 16 + 4).tobytes())  # length word
    f.write(np.int32(len(telescope_defs)).tobytes())  # number of telescopes
    # telescope definitions written as:
    # x1 x2 ... xN y1 y2 ... yN z1 z2 ... zN r1 r2 ... rN
    for tele in telescope_defs:
        f.write(np.float32(tele[0][0]).tobytes())
        f.write(np.float32(tele[0][1]).tobytes())
        f.write(np.float32(tele[0][2]).tobytes())
        f.write(np.float32(tele[2]).tobytes())

    # total number of photon bunches in the input
    total_bunches = 0
    
    # empty dataframe buffer
    buffer_df = pd.DataFrame()

    # chunk and event IDs
    chunk_id = 0
    ev_id = 0

    # load cherenkov data in chunks
    for chunk in cher_file.iter_batches(batch_size=chunk_size):
        # convert chunk to a dataframe
        chunk_df = chunk.to_pandas()

        # fill the buffer with transformed bunches (based on whether parallelization is enabled)
        if(parallel):
            buffer_df = pd.concat([buffer_df, chunk_df.parallel_apply(generate_bytearray, axis=1, result_type="expand")], ignore_index=True)
        else:
            buffer_df = pd.concat([buffer_df, chunk_df.apply(generate_bytearray, axis=1, result_type="expand")], ignore_index=True)

        # get min and max event id in this data chunk
        ev_id_max = buffer_df.max()["shower"]
 
        # write events
        while (ev_id_max > ev_id or ev_id == (n_events-1)):
            # filter buffer data for the requested event
            event_data = buffer_df[buffer_df["shower"] == ev_id]

            # report progress
            if (ev_id != 0 and ev_id % event_print_number == 0):
                print(f"   [{'{:5.1f}'.format(ev_id/n_events*100)}%] converted {ev_id}/{n_events} events ({total_bunches} bunches)")

            # correct the event number and the first interaction altitude
            event_header_bytes[4:8] = np.float32(ev_id).tobytes()
            event_header_bytes[24:28] = np.float32(first_ints[ev_id]).tobytes()

            # EVENT HEADER
            f.write(sync_marker)  # sync marker
            f.write(np.int32(type_event_header).tobytes())  # type/version word
            f.write(np.int32(id_word).tobytes())  # ID word
            f.write(np.int32(header_size_m).tobytes())  # length word
            f.write(np.int32(header_size).tobytes())  # number of floats in header/end
            f.write(event_header_bytes)  # write event header

            # ARRAY OFFSETS
            f.write(sync_marker)  # sync marker
            f.write(np.int32(type_array_offsets).tobytes())  # type/version word
            f.write(np.int32(id_word).tobytes())  # ID word
            f.write(np.int32(len(array_offsets) * 12 + 4).tobytes())  # length word
            f.write(np.int32(len(array_offsets)).tobytes())  # number of offsets (i.e. number of arrays?)
            # array offsets as:
            # t1 t2 ... tN x1 x2 ... xN y1 y2 ... yN 
            for par in range(3):
                for offset in array_offsets:
                    f.write(np.float32(offset[par]).tobytes())

            # number of photon bunches and photons in this event
            n_bunch_event = event_data.shape[0]
            n_photons_event = n_bunch_event * photon_bunching

            # TELESCOPE DATA
            f.write(sync_marker)  # sync marker
            f.write(np.int32(type_tele_data).tobytes())  # type/version word
            f.write(np.int32(id_word).tobytes())  # ID word
            # length word
            # the TelescopeDefinitions object contains only subobjects, so bit 30 of the length word has to be set
            # actual length is 
            #   = n_bunches * 32 (each bunch is 8 x 4-byte)
            #   + n_telescopes * 24 (one bunch object per telescope, 12-byte bunch object header + 12-byte bunch object prefix)
            #   and also add 1073741824 which sets bit 30
            f.write(np.int32(n_bunch_event * 32 + len(telescope_defs) * 24 + 1073741824).tobytes())  # length word

            # analyze number of telescopes and bunches in events:
            for tele_id in range(len(telescope_defs)):
                # filter cherenkov data in this event for this telescope
                tele_data = event_data[event_data["obsId"] == tele_id]

                if (test):
                    for bunch in test_bunches:
                        # check if this event contains a testing bunch
                        if (bunch[0] == ev_id and bunch[1] == tele_id):

                            # select a random bunch in this event
                            bunch[2] = random.randrange(0, tele_data.shape[0])

                            # get the selected bunch
                            ref_bunch = tuple(tele_data.values[bunch[2]][2:10])
                            
                            # add it to the list
                            bunches_reference.append(ref_bunch)

                # number of bunches in the event for this telescope
                n_bunch_tele = tele_data.shape[0]
                n_photons_tele = n_bunch_tele * photon_bunching

                # BUNCHES
                # not a top-level object, no sync marker
                f.write(np.int32(type_bunch).tobytes())  # type/version word
                f.write(np.int32(id_word).tobytes())  # ID word
                f.write(np.int32(n_bunch_tele * 32 + 12).tobytes())  # length word, 16-byte per bunch + 12-byte header
                # bunch object prefix length is 12 bytes:
                #   = prefix for array and telescope ID (2 x 2-byte int)
                #   + number of photons (4-byte float),
                #   + number of bunches (4-byte int)
                f.write(np.int16(0).tobytes())  # array ID always 0
                f.write(np.int16(tele_id).tobytes())
                f.write(np.float32(n_photons_tele).tobytes())
                f.write(np.int32(n_bunch_tele).tobytes())

                # write photon bunches
                for bunch in tele_data["bytearray"].values.tolist():
                    f.write(bunch)

                total_bunches += n_bunch_tele

            # drop rows for this already written events from the buffer
            buffer_df.drop(buffer_df[buffer_df["shower"] == ev_id].index, inplace=True)

            # EVENT END
            f.write(sync_marker) # sync marker
            f.write(np.int32(type_event_end).tobytes())  # type/version word
            f.write(np.int32(id_word).tobytes())  # ID word
            f.write(np.int32(header_size_m).tobytes())  # length word
            f.write(np.int32(header_size).tobytes())  # number of floats in header/end
            # correct the event number
            event_end_bytes[4:8] = np.float32(ev_id).tobytes()
            f.write(event_end_bytes)  # write event end

            ev_id += 1
        
        chunk_id += 1

    print(f"   [100.0%] converted {n_events}/{n_events} events ({total_bunches} bunches)")

    # RUN END
    f.write(sync_marker)  # sync marker
    f.write(np.int32(type_run_end).tobytes())  # type/version word
    f.write(np.int32(id_word).tobytes())  # ID word
    f.write(np.int32(16).tobytes())  # number of floats in header/end
    f.write(np.int32(3).tobytes())  # number of floats in run end (always 3)
    # correct the number of events
    run_end_bytes[8:12] = np.float32(n_events).tobytes()
    f.write(run_end_bytes) 

print(f"Opening and trying to read the created binary file")
with eventio.IACTFile(path_output) as f:
    if(debug):
        print("   Opened successfully")

    # test run header
    if(debug):
        print(f"   Run header:")
        print(f"      CORSIKA version : {f.header["version"]}")
        print(f"      Showers         : {f.header["n_showers"]}")
        print(f"      Energy range    : {f.header["energy_min"]} - {f.header["energy_max"]}")
        print(f"      Obs. level      : {f.header["observation_height"][0] / 1e2} m")

    # test input card - print first five lines
    input_card = f.input_card.decode("utf-8").split("\n")
    if(debug):
        print(f"   Input card header:")
        for i in range(5):
            print(f"      {input_card[i]}")
        if len(input_card) > 5:
            print(f"      ...")
    
    # test telescope definitions    
    n_telescopes = len(f.telescope_positions)
    if(debug):
        print(f"   Telescopes ({n_telescopes}):")
    for telescope in range(n_telescopes):
        radius = f.telescope_positions[telescope]["r"] / 1e2
        if(debug):
            print(f"      [{telescope}] position : ({f.telescope_positions[telescope]["x"] / 1e2}, {f.telescope_positions[telescope]["y"]/1e2}, {f.telescope_positions[telescope]["z"]/1e2}) m")
            print(f"          radius   : {radius} m")

    # test reading event
    if(debug):
        print("   Iterating events:")
    for event in f:
        # event number
        ev_id = int(event.header["event_number"])

        # print info only for the first event
        if (debug and ev_id < 1):
            print(f"      [{ev_id}] energy       : {event.header["total_energy"]} GeV")
            print(f"      [{ev_id}] injection height: {event.header["starting_height"] / 1e2} m")
            print(f"      [{ev_id}] 1st int. alt : {event.header["first_interaction_height"] / 1e2} m")
        
        for tele_id, bunches in event.photon_bunches.items():
            if (debug and ev_id < 1):
                print(f"      [{ev_id}] photon bunches: telescope {tele_id}:")    

            bunch_id = 0
            for bunch in bunches:
                # print info only for the first three bunches
                if (debug and ev_id < 1 and bunch_id < 10):
                    precision = 4
                    print(f"          [{format(bunch_id):.{precision}}] x = {bunch["x"]:.{precision}} cm,   y = {bunch["y"]:.{precision}} cm, cx = {bunch["cx"]:.{precision}}, cy = {bunch["cy"]:.{precision}}")
                    print(f"              t = {bunch["time"]} ns, zem = {bunch["zem"] / 1e2:.{precision+2}} m, ph = {bunch["photons"]:.{precision}}, wl = {bunch["wavelength"]:.{precision}}")        
                bunch_id += 1

        if (test):
            for bunch in test_bunches:
                # check if this event contains a test bunch
                if (bunch[0] == ev_id):
                    # get the test bunch
                    conv_bunch = tuple(event.photon_bunches[tele_id][bunch[2]])
                    
                    # add bunch to list
                    bunches_converted.append(conv_bunch)
                
print(f"Read all events successfully")

# evaluate bunch conversion tests
if (test and n_tests > 0):
    print(f"Testing conversion of {n_tests} randomly selected bunches:")

    # maximum difference between reference and converted value
    max_diff = np.float64(0)

    # go over test bunches
    for b in range(n_tests):
        for i in range(bunch_size):
            # get the difference between reference and converted value
            diff = np.abs(np.float64(bunches_reference[b][i]) / np.float64(bunches_converted[b][i]) - 1)
            # store the maximum value
            max_diff = max(diff, max_diff)

    print(f"   Maximum difference between original and converted values: {max_diff}\n")

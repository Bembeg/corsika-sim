# script to convert CORSIKA 8 simulation files containing Cherenkov photon
# information (i.e. input) to the EventIO format (i.e. output)

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

def generate_run_header(version):
    if debug:
        print("Generating run header")

    # run header - 273 floats
    run_header = np.zeros(273).astype(np.float32) 

    # observation level
    with open(path_input + "/particles/config.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
        header_obs_level = np.float32(np.linalg.norm(content["plane"]["center"]))

    with open(path_input + "/primary/summary.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
        energies_primary = [content[shower]["total_energy"] for shower in content]
        header_ene_min = min(energies_primary)
        header_ene_max = max(energies_primary)
        header_n_show = len(content)

    # manually define some values for the run header
    header_version = np.float32(version)
    header_date = np.float32(0)
    header_n_obs_levels = np.float32(1)
  
    # put values into the run header - for reference, see run_header_fields object in corsikaio/subblocks/run_header.py
    run_header[2] = header_date
    run_header[3] = header_version
    run_header[4] = header_n_obs_levels
    run_header[5] = header_obs_level
    run_header[16] = header_ene_min
    run_header[17] = header_ene_max
    run_header[92] = header_n_show

    if (debug):
        print(f"   date       : {header_date}")
        print(f"   version    : {header_version}")
        print(f"   obs. level : {header_obs_level}")
        print(f"   energy min : {header_ene_min}")
        print(f"   energy max : {header_ene_max}")
        print(f"   showers    : {header_n_show}")

    # convert header to bytearray
    run_header_bytes = bytearray(run_header)
    run_header_bytes[0:4] = b"RUNH"

    return run_header_bytes

def generate_event_header(event_number, version):
    if debug:
        print(f"Generating event header for event {event_number}")

    event_header = np.zeros(273).astype(np.float32)
    
    # observation level
    with open(path_input + "/particles/config.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
        header_obs_level = np.float32(np.linalg.norm(content["plane"]["center"]))

    # mapping of primary particle IDs from CORSIKA8 to CORSIKA7 
    # TODO proton number?
    pid_map = {"Photon": 1, "Proton": 2}

    # primary energies
    with open(path_input + "/primary/summary.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
        header_total_energy = np.float32(content["shower_" + str(event_number)]["total_energy"])
        header_pid = np.float32(pid_map[content["shower_" + str(event_number)]["name"]])    

        prim_x = content["shower_" + str(event_number)]["x"]
        prim_y = content["shower_" + str(event_number)]["y"]
        prim_z = content["shower_" + str(event_number)]["z"]
        header_start_height = header_obs_level + np.float32(np.linalg.norm([prim_x, prim_y, prim_z]))

    # manually define values for the event header
    header_event_number = np.float32(event_number)
    header_version = np.float32(version)
    header_n_obs_levels = np.float32(1)
    # TODO calculate momentum vector
    header_mom_x = np.float32(0)
    header_mom_y = np.float32(0)
    header_mom_mz = header_total_energy
    # TODO calculate zenith, azimuth, theta, phi
    header_zenith = np.float32(0)
    header_azimuth = np.float32(0)
    header_theta = np.float32(0)
    header_phi = np.float32(0)
    # TODO cherenkov parameters from config
    header_cher_bunch = np.float32(5)
    header_cher_wavelen_min = np.float32(300)
    header_cher_wavelen_max = np.float32(800)

    # put values into the run header - for reference, see run_header_fields object in corsikaio/subblocks/run_header.py
    event_header[1] = header_event_number
    event_header[2] = header_pid
    event_header[3] = header_total_energy
    event_header[7] = header_mom_x
    event_header[8] = header_mom_y
    event_header[9] = header_mom_mz
    event_header[10] = header_zenith
    event_header[11] = header_azimuth
    event_header[45] = header_version
    event_header[46] = header_n_obs_levels
    event_header[47] = header_obs_level
    event_header[58] = header_total_energy
    event_header[59] = header_total_energy
    event_header[80] = header_theta
    event_header[81] = header_theta
    event_header[82] = header_phi
    event_header[83] = header_phi
    event_header[84] = header_cher_bunch
    event_header[95] = header_cher_wavelen_min
    event_header[96] = header_cher_wavelen_max
    event_header[157] = header_start_height

    # convert header to bytearray
    event_header_bytes = bytearray(event_header)
    event_header_bytes[0:4] = b"EVTH"

    if (debug):
        print(f"   event number  : {event_number}")
        print(f"   PID           : {header_pid}")
        print(f"   total energy  : {header_total_energy}")
        print(f"   mom x         : {header_mom_x}")
        print(f"   mom y         : {header_mom_y}")
        print(f"   -mom z        : {header_mom_mz}")
        print(f"   azimuth       : {header_azimuth}")
        print(f"   zenith        : {header_zenith}")
        print(f"   obs. level    : {header_obs_level}")
        print(f"   start height  : {header_start_height}")
        print(f"   theta         : {header_theta}")
        print(f"   phi           : {header_phi}")
        print(f"   cher. bunch   : {header_cher_bunch}")
        print(f"   cher. range   : {header_cher_wavelen_min} - {header_cher_wavelen_max}")
    return event_header_bytes

def generate_telescope_definitions():
    if debug:
        print(f"Generating telescope definitions")

    # telescope definions are formatted as [position, pointing, radius] - [[x,y,z], [pX,pY,pZ], r]
    telescope_defs = []

    with open(path_input + "/cherenkov/config.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
        # get telescope names
        names_tele = [tele for tele in content["observers"]]

        for tele in names_tele:
            # empty telescope definition
            telescope_def = []

            # get telescope position
            telescope_def.append(content["observers"][tele]["position"])
            # pointing direction
            telescope_def.append(content["observers"][tele]["pointing"])
            # and radius
            telescope_def.append(content["observers"][tele]["radius"])

            # append telescope definition to the list
            telescope_defs.append(telescope_def)

    if debug:
        teleID = 0
        for tele in telescope_defs:
            print(f"   [{teleID}] x={tele[0][0]}, y={tele[0][1]}, z={tele[0][2]}")
            print(f"   [{teleID}] px={tele[1][0]}, py={tele[1][1]}, pz={tele[1][2]}")
            print(f"   [{teleID}] r={tele[2]}")     

    return telescope_defs


def generate_array_offsets():
    if debug:
        print("Generating array offsets (all zeros)")

    # array offsets are defined as [t,x,y]
    array_offsets = []

    # assume one array with zero offsets in time and (x,y)
    array_offsets.append([0,0,0])

    if(debug):
        for array in range(len(array_offsets)):
            print(f"   [{array}] t={array_offsets[array][0]}, x={array_offsets[array][1]}, y={array_offsets[array][2]}")

    return array_offsets

def generate_input_card(version):
    if debug:
        print("Generating input card")

    # get CLI arguments passed to a CORSIKA 8 run
    with open(path_input + "/config.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
        args = content["args"]

    args_split = args.split()
    args_split.pop(0)

    input_card = [f"CORSIKA 8 ({version}) inputs:"]

    for i in range(len(args_split)):
        if args_split[i][0] == "-":
            
            arg_line = args_split[i].strip("-")

            # check that next one is not a par
            if args_split[i+1][0] != "-":
                arg_line += (" " + args_split[i+1])
                
            input_card.append(arg_line)

    # convert input card to eventIO strings and to a bytearray
    input_card_bytes = bytearray()
    for line in input_card:
        if debug:
            print(f"   {line}")

        # eventIO string format is a 2-byte-integer for length + the string itself
        input_card_bytes += np.int16(len(line)).tobytes()
        input_card_bytes += line.encode()

    return input_card_bytes, len(input_card)


def get_number_showers():
    with open(path_input + "/summary.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
    return content["showers"]

# debug mode
debug = False

# override the CORSIKA version to 8.0
version_override = 8.0

# check that path to C8 output was provided
if len(sys.argv) == 1:
    print("No CORSIKA 8 output provided")
    print_help()
    sys.exit(1)

# path to input
path_input = sys.argv[1]
print(f"Input path  : '{path_input}'")

# output file name
name_output = "data_eventIO.dat"

# path to output
if len(sys.argv) >= 3:
    # output name provided by user
    path_output = "output/" + sys.argv[2] + "/" + name_output
else:
    # store output in the input dir
    path_output = sys.argv[1] + "/" + name_output

print(f"Output path : '{path_output}'")

# paths to parquet and config files
path_cher_parquet = path_input + "/cherenkov/light.parquet"
path_cher_conf = path_input + "/cherenkov/config.yaml"

# check whether input files exist
if not (os.path.exists(path_cher_parquet) or os.path.exists(path_cher_conf)):
    print("Missing Cherenkov files (parquet or config) in input path")
    sys.exit(2)

# load input data file
cher_data = pd.read_parquet(path_cher_parquet, "pyarrow")

# load input config file
with open(path_cher_conf, "r") as read_file:
    cher_conf = yaml.safe_load(read_file)

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

word_size = 4

header_size = corsikaio.constants.BLOCK_SIZE_FLOATS
header_size_m = (header_size + 1) * word_size

# ID word serves as an additional object identifier, ignore and always set to 0
id_word = 0

# empty array of 273 floats (eventIO block)
data = np.zeros(273).astype(np.float32)

# generate the run header, override version to 8.0
run_header_bytes = generate_run_header(version=version_override)

# generate telescope definition object
telescope_defs = generate_telescope_definitions()

# generate array offsets
array_offsets = generate_array_offsets()

# generate input card
input_card_bytes, input_card_lines = generate_input_card(version=version_override)

# number of events (showers)
n_events = get_number_showers()

# # analyze number of telescopes and bunches in events:
# for evID in range(n_events):
#     print(f"event {evID}: ")
#     for teleID in range(len(telescope_defs)):
#         filtered_data = cher_data[(cher_data["shower"] == evID) & (cher_data["obsId"] == teleID)]
#         n_bunch = filtered_data.count()["hitX"]
#         print(f"   telescope {teleID}: {n_bunch} bunches")

print(f"\nWriting eventIO file")
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

    # write individual events (i.e. showers)
    for evID in range(n_events):
        print(f"   writing event {evID} ({evID+1}/{n_events})")

        # generate the event header, override version to 8.0
        event_header_bytes = generate_event_header(event_number=evID, version=version_override)

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
        # array offsets written as: (TODO I assume?)
        # t1 t2 ... tN x1 x2 ... xN y1 y2 ... yN
        for par in range(3):
            for offset in array_offsets:  
                f.write(np.float32(offset[par]).tobytes())

        # filter cherenkov data for this event
        event_data = cher_data[cher_data["shower"] == evID]

        # number of photon bunches and photons in this event
        n_bunch_event = event_data.count()["weight"]
        n_photons_event = event_data.sum()["weight"]
        # number of telescopes with hits in this event 
        n_tele_event = event_data.nunique()["obsId"]

        print(f"      {n_bunch_event} bunches, {n_photons_event} photons, {n_tele_event} telescopes")

        # TELESCOPE DATA
        f.write(sync_marker)  # sync marker
        f.write(np.int32(type_tele_data).tobytes())  # type/version word
        f.write(np.int32(id_word).tobytes())  # ID word
        # length word
        # The TelescopeDefinitions object contains only subobjects, so bit 30 of the length word has to be set.
        # Split the length word into two 2-byte words, first with the actual length, second to set the bit 30
        # Actual length is 
        #   = n_bunches * 16 (each bunch is 8 x 2-byte)
        #   + n_telescopes * 24 (one bunch object per telescope, 12-byte bunch object header + 12-byte bunch object prefix)
        f.write(np.int16(n_bunch_event * 16 + n_tele_event * 24).tobytes())  # length word
        f.write(np.int16(16384).tobytes())

        # analyze number of telescopes and bunches in events:
        for teleID in range(n_tele_event):
            # filter cherenkov data in this event for this telescope
            tele_data = event_data[event_data["obsId"] == teleID]

            # number of bunches in the event for this telescope
            n_bunch_tele = tele_data.count()["weight"]
            n_photons_tele = tele_data.sum()["weight"] 

            print(f"         telescope {teleID}: {n_bunch_tele} bunches, {n_photons_event} photons")

            # BUNCHES
            # not a top-level object, no sync marker
            f.write(np.int16(type_bunch).tobytes())  # type/version word
            f.write(np.int16(16000).tobytes())  # include version 16000 in the type/version word, needed to parse correctly
            f.write(np.int32(id_word).tobytes())  # ID word
            f.write(np.int32(n_bunch_tele * 16 + 12).tobytes())  # length word, 16-byte per bunch + 12-byte header
            # bunch object length is 12 bytes:
            #   = prefix for array and telescope ID (2 x 2-byte int)
            #   + number of photons (4-byte float),
            #   + number of bunches (4-byte int)
            f.write(np.int16(0).tobytes())
            f.write(np.int16(teleID).tobytes())
            f.write(np.float32(n_photons_tele).tobytes())
            f.write(np.int32(n_bunch_tele).tobytes())

            center = telescope_defs[teleID][0]
            pointing = telescope_defs[teleID][1]
            radius = telescope_defs[teleID][2]

            # print(center, pointing, radius)

            # calculate rotation matrix to transform points onto the ground plane
            rotation_matrix = rotation_matrix_from_vectors(pointing, [0, 0, 1])

            # write photon bunches
            for _, bunch in tele_data.iterrows():
                # extract bunch values from the dataframe
                hit = [bunch["hitX"], bunch["hitY"], bunch["hitZ"]]
                dir = [bunch["dirX"], bunch["dirY"], bunch["dirZ"]]
                time = bunch["time"]
                zem = bunch["emissionAlt"]
                photons = bunch["weight"]
                wavelength = bunch["wavelength"]

                # transform hits to observer local coordinate system
                trf_hits = np.dot(rotation_matrix, np.subtract(hit, center))
                trf_dirs = np.dot(rotation_matrix, dir)

                print(bunch)                
                
                # in compact mode each bunch is 8 x 2-byte int and can be modified by a factor, so we modify it the opposite way to counter the reader:
                #   x (divided by 10)
                #   y (divided by 10),
                #   cx (divided by 30000, clamped to [-1,1])
                #   cy (divided by 30000, clamped to [-1,1])
                #   time (divided by 10)
                #   zem (10 ^ (x/1000) for x)
                #   photons (divided by 100)
                #   wavelength
    
                bunch_array = [trf_hits[0] * 10, trf_hits[1] * 10, trf_dirs[0] * 30000, trf_dirs[1] * 30000, time * 10, np.log10(zem), photons * 100, wavelength], 
                print(bunch_array)
                
                # write bunch as a series of ones
                bunches_bytes = bytearray(np.array(bunch_array, dtype=np.int16))
                f.write(bunches_bytes)

        # EVENT END
        f.write(sync_marker)  # sync marker
        f.write(np.int32(type_event_end).tobytes())  # type/version word
        f.write(np.int32(id_word).tobytes())  # ID word
        f.write(np.int32(header_size_m).tobytes())  # length word
        f.write(np.int32(header_size).tobytes())  # number of floats in header/end
        event_end_bytes = bytearray(data)
        # modify bytearray to start with the EVTE mark
        event_end_bytes[0:4] = b"EVTE"
        # correct the event number
        event_end_bytes[4:8] = np.float32(evID).tobytes()
        f.write(event_end_bytes)

    # RUN END
    f.write(sync_marker)  # sync marker
    f.write(np.int32(type_run_end).tobytes())  # type/version word
    f.write(np.int32(id_word).tobytes())  # ID word
    f.write(np.int32(16).tobytes())  # number of floats in header/end
    f.write(np.int32(3).tobytes())  # number of floats in run end (always 3)
    run_end = bytearray(np.zeros(3).astype(np.float32)) 
    # modify bytearray to start with the RUNE mark
    run_end[0:4] = b"RUNE"
    # correct the number of events
    run_end[8:12] = np.float32(n_events).tobytes()
    f.write(run_end) 

print(f"\nOpening the created binary file '{path_output}")
with eventio.IACTFile(path_output) as f:
    print("   Opened successfully")

    # test run header
    print(f"   Run header:")
    print(f"      CORSIKA version : {f.header["version"]}")
    print(f"      Showers         : {f.header["n_showers"]}")
    print(f"      Energy range    : {f.header["energy_min"]} - {f.header["energy_max"]}")
    print(f"      Obs. level      : {f.header["observation_height"][0]}")

    # test input card - print first five lines
    input_card = f.input_card.decode("utf-8").split("\n")
    print(f"   Input card header:")
    for i in range(5):
        print(f"      {input_card[i]}")
    if len(input_card) > 5:
        print(f"      ...")
    
    # test telescope definitions    
    n_telescopes = len(f.telescope_positions)
    print(f"   Telescopes ({n_telescopes}):")
    for telescope in range(n_telescopes):
        radius = f.telescope_positions[telescope]["r"] / 1e2
        print(f"      [{telescope}] position : ({f.telescope_positions[telescope]["x"] / 1e2}, {f.telescope_positions[telescope]["y"]/1e2}, {f.telescope_positions[telescope]["z"]/1e2}) m")
        print(f"          radius   : {radius} m")

    # test event header
    print("   Iterating events:")
    for event in f:
        evID = int(event.header["event_number"])
        start_alt = (event.header["starting_height"] + event.header["first_interaction_height"]) / 1e2

        print(f"   Event header:")
        print(f"      [{evID}] energy       : {event.header["total_energy"]} GeV")
        print(f"      [{evID}] 1st int. alt : {start_alt} m")
        
        print(f"   Photon bunches:")
        bunches = event.photon_bunches
        
        for teleID, bunches in event.photon_bunches.items():
            print(f"      Telescope {teleID}:")    
        
            bunchID = 0
            # for bunch in range(len(bunches)):
            for bunch in bunches:
                print(f"         [{"{0:2d}".format(bunchID)}] x = {"{0:3f}".format(bunch["x"])},   y = {"{0:3f}".format(bunch["y"])}, cx = {"{0:3f}".format(bunch["cx"])}, cy = {"{0:3f}".format(bunch["cy"])}")
                print(f"              t = {"{0:3f}".format(bunch["time"])}, zem = {"{0:3f}".format(bunch["zem"])}, ph = {"{0:3f}".format(bunch["photons"])}, wl = {"{0:3f}".format(bunch["wavelength"])}")        
                bunchID += 1

# # process photon data
# for observer_name in conf["observers"]:
#     print(f"Processing data for telescope '{observer_name}'")

#     center = conf["observers"][observer_name]["position"]
#     pointing = conf["observers"][observer_name]["pointing"]
#     radius = conf["observers"][observer_name]["radius"]
    
#     # filter dataframe for this observer only
#     filtered_data = data[data["obsId"] == observer_idx]
    
#     # calculate rotation matrix to transform points onto the ground plane
#     rotation_matrix = rotation_matrix_from_vectors(pointing, [0, 0, 1])

#     # hits in the global coordinate system
#     hits = [filtered_data["hitX"] - center[0], filtered_data["hitY"] - center[1], filtered_data["hitZ"] - center[2]]
#     # transform hits to observer local coordinate system
#     trf_hits = np.dot(rotation_matrix, hits)

#     # hit positions in cm
#     x = trf_hits[0] * 1e2
#     y = trf_hits[1] * 1e2

#     # hit directions in the global coordinate system
#     directions = [filtered_data["dirX"], filtered_data["dirY"], filtered_data["dirZ"]]
#     # transform directiosn to observer local coordinate system
#     trf_directions = np.dot(rotation_matrix, directions)
    
#     # calculate norms of direction vectors (should be unity, but making sure)
#     direction_norms = np.sqrt(trf_directions[0] * trf_directions[0] + trf_directions[1] * trf_directions[1] + trf_directions[2] * trf_directions[2])

#     # direction cosines
#     cx = trf_directions[0] / direction_norms
#     cy = trf_directions[1] / direction_norms

#     # arrival time
#     time = filtered_data["time"]

#     # emission altitude in cm
#     zem = filtered_data["emissionAlt"] * 1e2

#     # number of photons in the bunch
#     photons = filtered_data["weight"]

#     # wavelength
#     wavelength = filtered_data["wavelength"]

#     # check lengths of all data arrays
#     print("  data array lengths:")
#     print(f"            x : {len(x)}")
#     print(f"            y : {len(y)}")
#     print(f"           cx : {len(cx)}")
#     print(f"           cy : {len(cy)}")
#     print(f"         time : {len(time)}")
#     print(f"          zem : {len(zem)}")
#     print(f"      photons : {len(photons)}")
#     print(f"   wavelength : {len(wavelength)}")

#     observer_idx += 1

#     bunches = []
#     for i in range(len(x)):
#         bunch = (x[i], y[i], cx[i], cy[i], time[i], zem[i], photons[i], wavelength[i])
#         bunches.append(bunch)

#     bunches_array = np.array(bunches, dtype=dtype_bunch)





# script to convert CORSIKA 8 simulation files containing Cherenkov photon
# information (i.e. input) to the EventIO format (i.e. output)

import os
import sys
import yaml
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

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

    # write the header tag
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

    # header_start_height = obs_alt + np.float32(np.linalg.norm([prim_x, prim_y, prim_z]) * 1e2)
    start_point = np.add(content_particles["plane"]["center"], [prim_x, prim_y, prim_z])

    # primary particle momentum    
    header_mom_x = content_int_sum["shower_0"]["px"]
    header_mom_y = content_int_sum["shower_0"]["py"]
    header_mom_mz = content_int_sum["shower_0"]["pz"]

    # iterate over showers to collect first interaction altitudes
    for ev_id in range(n_events):
        first_int = [content_int_sum["shower_" + str(ev_id)]["x"], content_int_sum["shower_" + str(ev_id)]["y"], content_int_sum["shower_" + str(ev_id)]["z"]]

        # first interaction height
        first_int_height = np.float32(np.linalg.norm(np.add(content_particles["plane"]["center"], first_int)))
        first_int_alt = (first_int_height - np.linalg.norm(content_particles["plane"]["center"])) 

        # first interaction height stored in m, convert to cm and make negative (for some reason C7 stores the number as negative)
        first_ints.append(-first_int_alt * 1e2)

    # manually define values for the event header
    header_version = np.float32(version)
    header_n_obs_levels = np.float32(1)

    # TODO calculate zenith, azimuth, theta, phi
    header_zenith = np.float32(0)
    header_azimuth = np.float32(0)
    header_theta = np.float32(0)
    header_phi = np.float32(0)

    # TODO cherenkov parameters from config
    header_cher_bunch = np.float32(5)
    header_cher_wavelen_min = np.float32(240)
    header_cher_wavelen_max = np.float32(1000)
    
    # put values into the event header - for reference, see event_header_fields object in corsikaio/subblocks/event_header.py
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
        print(f"   PID            : {header_pid}")
        print(f"   total energy   : {header_total_energy} GeV")
        print(f"   mom x          : {header_mom_x} GeV/c")
        print(f"   mom y          : {header_mom_y} GeV/c")
        print(f"   -mom z         : {header_mom_mz} GeV/c")
        print(f"   azimuth        : {header_azimuth} rad")
        print(f"   zenith         : {header_zenith} rad")
        print(f"   obs. level     : {header_obs_level} cm")
        print(f"   start height   : {header_start_height} cm")
        print(f"   1st int.       : {first_ints[-1]} cm")
        print(f"   theta          : {header_theta} deg")
        print(f"   phi            : {header_phi} deg")
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

        # get telescope position
        telescope_def.append(np.multiply(content_cherenkov["observers"][tele]["position"], 1e2))
        # subtract observation level
        telescope_def[-1][2] -= obs_height
        # pointing direction
        telescope_def.append(content_cherenkov["observers"][tele]["pointing"])
        # and radius
        telescope_def.append(content_cherenkov["observers"][tele]["radius"] * 1e2)

        # append telescope definition to the list
        telescope_defs.append(telescope_def)

        # calculate rotation matrix
        rotation_matrices.append(rotation_matrix_from_vectors(content_cherenkov["observers"][tele]["pointing"], [0, 0, 1]))

    if debug:
        teleID = 0
        for tele in telescope_defs:
            print(f"   [{teleID}] x = {tele[0][0]}, y = {tele[0][1]}, z = {tele[0][2]} cm")
            print(f"   [{teleID}] px = {tele[1][0]}, py = {tele[1][1]}, pz = {tele[1][2]}")
            print(f"   [{teleID}] r = {tele[2]} cm")     

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
        gamma = content["shower_0"]["total_energy"] / 0.938272089
        beta = np.sqrt(1 - 1 / (gamma * gamma))

    # time to observation plane center
    time_to_obs = dist_to_obs / (0.299792458 * beta)

    # there will be only one array from CORSIKA 8
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

    args_split = content["args"].split()

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

def get_number_showers():
    with open(path_input + "/summary.yaml", "r") as read_file:
        content = yaml.safe_load(read_file)
    return content["showers"]


print("[Parquet-EventIO convertor for CORSIKA 8]")

# debug mode
debug = True

# override the CORSIKA version to 8.0
version_override = 8.0

# check that path to C8 output was provided
if len(sys.argv) == 1:
    print("No CORSIKA 8 output provided")
    print_help()
    sys.exit(1)

# path to input
path_input = sys.argv[1]
print(f"   Input path  : '{path_input}'")

# output file name
name_output = "data_eventIO.dat"

# path to output
if len(sys.argv) >= 3:
    # output name provided by user
    path_output = sys.argv[2]
else:
    # store output in the input dir
    path_output = sys.argv[1] + "/" + name_output

print(f"   Output path : '{path_output}'")

# paths to parquet and config files
path_cher_parquet = path_input + "/cherenkov/light.parquet"
path_cher_conf = path_input + "/cherenkov/config.yaml"

# check whether input files exist
if not (os.path.exists(path_cher_parquet) or os.path.exists(path_cher_conf)):
    print("   Missing Cherenkov files (parquet or config) in input path")
    sys.exit(2)

# load input data file
# cher_data = pd.read_parquet(path_cher_parquet, "pyarrow")
cher_file = pq.ParquetFile(path_cher_parquet)

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

header_size = corsikaio.constants.BLOCK_SIZE_FLOATS
header_size_m = (header_size + 1) * word_size

# ID word serves as an additional object identifier, ignore and always set to 0
id_word = 0

print("Generating headers and EventIO metadata")

# generate the run header, override version to 8.0
run_header_bytes = generate_run_header(version=version_override)

# generate the event header, override version to 8.0
event_header_bytes, first_ints = generate_event_header(version=version_override)

# generate telescope definition object
telescope_defs, rotation_matrices = generate_telescope_definitions()

# generate array offsets
array_offsets = generate_array_offsets()

# generate input card
input_card_bytes, input_card_lines = generate_input_card(version=version_override)

# generate event end
event_end_bytes = generate_event_end()

# generate run end
run_end_bytes = generate_run_end()

# number of events (showers)
n_events = get_number_showers()

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

    total_bunches = 0
    # write individual events (i.e. showers)

    event_data_ = pd.DataFrame()
    chunk_id = 0
    ev_id = 0

    # load cherenkov data in bunches
    for chunk in cher_file.iter_batches():
        # print(f"   processing chunk {chunk_id}, looking for event {ev_id}")
        
        # print(f"      event dataframe currently has {event_data_.shape[0]} bunches")
        
        chunk_df = chunk.to_pandas()

        # Min and max event id in this data chunk
        ev_id_min = chunk_df.min()["shower"]
        ev_id_max = chunk_df.max()["shower"]

        # print(f"      chunk min event ID: {ev_id_min}, max event ID: {ev_id_max}", end="")

        chunk_id += 1

        if (ev_id_min <= ev_id and ev_id_max >= ev_id):
            # print(" ... GOOD CHUNK")
            if event_data_.shape[0] == 0:
                event_data_ = chunk_df
            else:
                event_data_ = pd.concat([event_data_, chunk_df], ignore_index=True)

        while (ev_id_max > ev_id):
            print(f"writing event {ev_id}")

            # filter cherenkov data for this event
            event_data = event_data_[event_data_["shower"] == ev_id]

            # keep this chunk for the next event
            event_data_ = chunk_df

            if (ev_id != 0 and ev_id % int(n_events/40) == 0):
                print(f"   [{'{:5.1f}'.format(ev_id/n_events*100)}%] written {ev_id}/{n_events} events ({total_bunches} bunches)")

            # correct the event number and the first interaction height
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
            # array offsets written as: (TODO I assume?)
            # t1 t2 ... tN x1 x2 ... xN y1 y2 ... yN
            for par in range(3):
                for offset in array_offsets:
                    f.write(np.float32(offset[par]).tobytes()) 

            # if (ev_id > 2 and ev_id < 5):
            #     print(event_data)

            # number of photon bunches and photons in this event
            n_bunch_event = event_data.count()["weight"]
            n_photons_event = event_data.sum()["weight"]

            # if (ev_id > 2 and ev_id < 5):
            #     print(f"      {ev_id}  {n_bunch_event} bunches, {n_photons_event} photons")

            # TELESCOPE DATA
            f.write(sync_marker)  # sync marker
            f.write(np.int32(type_tele_data).tobytes())  # type/version word
            f.write(np.int32(id_word).tobytes())  # ID word
            # length word
            # The TelescopeDefinitions object contains only subobjects, so bit 30 of the length word has to be set.
            # Actual length is 
            #   = n_bunches * 16 (each bunch is 8 x 2-byte)
            #   + n_telescopes * 24 (one bunch object per telescope, 12-byte bunch object header + 12-byte bunch object prefix)
            #   and also add 1073741824 which flips bit 30
            f.write(np.int32(n_bunch_event * 32 + len(telescope_defs) * 24 + 1073741824).tobytes())  # length word

            # analyze number of telescopes and bunches in events:
            for teleID in range(len(telescope_defs)):
                # filter cherenkov data in this event for this telescope
                tele_data = event_data[event_data["obsId"] == teleID]

                # number of bunches in the event for this telescope
                n_bunch_tele = int(tele_data.count()["weight"])
                n_photons_tele = tele_data.sum()["weight"] 

                # if (ev_id > 2 and ev_id < 5):
                #     print(f"         telescope {teleID}: {n_bunch_tele} bunches, {n_photons_event} photons")

                # BUNCHES
                # not a top-level object, no sync marker
                f.write(np.int16(type_bunch).tobytes())  # type/version word
                f.write(np.int16(0).tobytes())  # include version 16000 in the type/version word, needed to parse correctly
                f.write(np.int32(id_word).tobytes())  # ID word
                f.write(np.int32(n_bunch_tele * 32 + 12).tobytes())  # length word, 16-byte per bunch + 12-byte header
                # bunch object length is 12 bytes:
                #   = prefix for array and telescope ID (2 x 2-byte int)
                #   + number of photons (4-byte float),
                #   + number of bunches (4-byte int)
                f.write(np.int16(0).tobytes())  # array ID always 0
                f.write(np.int16(teleID).tobytes())
                f.write(np.float32(n_photons_tele).tobytes())
                f.write(np.int32(n_bunch_tele).tobytes())

                # write photon bunches
                for _, bunch in tele_data.iterrows():
                    # extract bunch values from the dataframe
                    hit = np.multiply([bunch["hitX"], bunch["hitY"], bunch["hitZ"]], 1e2)
                    dir = [bunch["dirX"], bunch["dirY"], bunch["dirZ"]]

                    # transform hits to observer local coordinate system
                    trf_hits = np.dot(rotation_matrices[teleID], np.subtract(hit, telescope_defs[teleID][0]))
                    trf_dirs = np.dot(rotation_matrices[teleID], dir)

                    bunch_array = [trf_hits[0], trf_hits[1], trf_dirs[0], trf_dirs[1],
                    bunch["time"] - array_offsets[0][0], bunch["emissionAlt"] * 1e2,
                    bunch["weight"], bunch["wavelength"]] 

                    # try converting the array to float32 bytearray, watching for overflow
                    try:
                        bunches_bytes = bytearray(np.array(bunch_array, dtype=np.float32))
                    except OverflowError:
                        print(f"Photon bunch has a value outside of np.int16 range in event {ev_id}: ", end="")

                        for i in range(len(bunch_array)):
                            if (bunch_array[i] < np.iinfo(np.float32).min):                      
                                print(f"array element {i} clamped ({bunch_array[i]} -> {np.iinfo(np.float32).min})")
                                bunch_array[i] = np.iinfo(np.float32).min
                            elif (bunch_array[i] > np.iinfo(np.float32).max):
                                print(f"array element {i} clamped ({bunch_array[i]} -> {np.iinfo(np.float32).max})")
                                bunch_array[i] = np.iinfo(np.float32).max

                    f.write(bunches_bytes)

                    total_bunches += 1

            # EVENT END
            f.write(sync_marker)  # sync marker
            f.write(np.int32(type_event_end).tobytes())  # type/version word
            f.write(np.int32(id_word).tobytes())  # ID word
            f.write(np.int32(header_size_m).tobytes())  # length word
            f.write(np.int32(header_size).tobytes())  # number of floats in header/end
            # correct the event number
            event_end_bytes[4:8] = np.float32(ev_id).tobytes()
            f.write(event_end_bytes)

            ev_id += 1

    print(f"   [100%] written {n_events}/{n_events} events ({total_bunches} bunches)")

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

    # test event
    if(debug):
        print("   Iterating events:")
    for event in f:
        # event number
        ev_id = int(event.header["event_number"])

        # print(f"event{ev_id}")

        # print info only for the first event
        if (debug and ev_id < 1):
            print(f"      [{ev_id}] energy       : {event.header["total_energy"]} GeV")
            print(f"      [{ev_id}] injection height: {event.header["starting_height"] / 1e2} m")
            print(f"      [{ev_id}] 1st int. alt : {event.header["first_interaction_height"] / 1e2} m")
        
        for teleID, bunches in event.photon_bunches.items():
            if (debug and ev_id < 1):
                print(f"      [{ev_id}] photon bunches: telescope {teleID}:")    
        
            bunch_id = 0
            for bunch in bunches:
                # print info only for the first three bunches
                if (debug and ev_id < 1 and bunch_id < 10):
                    precision = 4
                    print(f"          [{format(bunch_id):.{precision}}] x = {bunch["x"]:.{precision}} cm,   y = {bunch["y"]:.{precision}} cm, cx = {bunch["cx"]:.{precision}}, cy = {bunch["cy"]:.{precision}}")
                    print(f"              t = {bunch["time"]} ns, zem = {bunch["zem"] / 1e2:.{precision+2}} m, ph = {bunch["photons"]:.{precision}}, wl = {bunch["wavelength"]:.{precision}}")        
                bunch_id += 1
print(f"Read successfully\n")
  
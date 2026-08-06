import numpy as np
import eventio
import gzip

import corsikaio

# path to create the dummy file at
path = "dummyfile.dat"

# empty array of 273 floats (eventIO block?)
data = np.zeros(273).astype(np.float32)

# run header
run_header = np.zeros(273).astype(np.float32)

# manually define values for the run header
header_version = np.float32(8.0)
header_date = np.float32(0)
header_n_obs_levels = np.float32(1)
header_obs_level = np.float32(2000)
header_ene_min = np.float32(8)
header_ene_max = np.float32(15)
header_cut_had = np.float32(0.1)
header_cut_muo = np.float32(0.1)
header_cut_ele = np.float32(0.1)
header_cut_pho = np.float32(0.1)
header_n_show = np.float32(1)

# put values into the run header - for reference, see run_header_fields object in corsikaio/subblocks/run_header.py
run_header[2] = header_date
run_header[3] = header_version
run_header[4] = header_n_obs_levels
run_header[5] = header_obs_level
run_header[16] = header_ene_min
run_header[17] = header_ene_max
run_header[20] = header_cut_had
run_header[21] = header_cut_muo
run_header[22] = header_cut_ele
run_header[23] = header_cut_pho
run_header[92] = header_n_show

# convert header to bytearray
run_header_bytes = bytearray(run_header)
run_header_bytes[0:4] = b"RUNH"

# telescope definitions - [x,y,z,r] list for each telescope
tele_def = [[1, 2, 3, 4], [5,6,7,8]]

# event header
event_header = np.zeros(273).astype(np.float32)

# manually define values for the event header
header_pid = 1
header_total_energy = np.float32(10)
header_start_height = np.float32(12000000)
header_first_target_id = np.float32(0)
header_first_int_alt = np.float32(-3500000)
header_mom_x = np.float32(0)
header_mom_y = np.float32(0)
header_mom_mz = np.float32(10)
header_zenith = np.float32(0)
header_azimuth = np.float32(0)
header_theta_min = np.float32(0)
header_theta_max = np.float32(0)
header_phi_min = np.float32(0)
header_phi_max = np.float32(0)
header_cher_bunch = np.float32(5)
header_cher_wavelen_min = np.float32(200)
header_cher_wavelen_max = np.float32(800)

# put values into the run header - for reference, see run_header_fields object in corsikaio/subblocks/run_header.py
event_header[2] = header_pid
event_header[3] = header_total_energy
event_header[5] = header_first_target_id
event_header[6] = header_first_int_alt
event_header[7] = header_mom_x
event_header[8] = header_mom_y
event_header[9] = header_mom_mz
event_header[10] = header_zenith
event_header[11] = header_azimuth
event_header[45] = header_version
event_header[46] = header_n_obs_levels
event_header[47] = header_obs_level
event_header[58] = header_ene_min
event_header[59] = header_ene_max
event_header[60] = header_cut_had
event_header[61] = header_cut_muo
event_header[62] = header_cut_ele
event_header[63] = header_cut_pho
event_header[80] = header_theta_min
event_header[81] = header_theta_max
event_header[82] = header_phi_min
event_header[83] = header_phi_max
event_header[84] = header_cher_bunch
event_header[95] = header_cher_wavelen_min
event_header[96] = header_cher_wavelen_max
event_header[157] = header_start_height

# convert header to bytearray
event_header_bytes = bytearray(event_header)
event_header_bytes[0:4] = b"EVTH"

# offsets for arrays - t, x, y
array_offsets = [[1, 2, 3]]

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

# ID word serves as an additional identifier, ignore and set to 0
id_word = 0

# load input card template
with open("template_input_card.txt", "r") as input_card:
    data_input_card = input_card.readlines()
    lines_input_card = len(data_input_card)

# convert input card to eventIO strings and to a bytearray
input_card_bytearray = bytearray()
for line in data_input_card:
    # remove newline character
    line_strip = line.strip()
    # eventIO string format is a 2-byte-integer for length + the string itself
    input_card_bytearray += np.int16(len(line_strip)).tobytes()
    input_card_bytearray += line_strip.encode()

with open(path, 'wb') as f:
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
    f.write(np.int32(len(input_card_bytearray) + 4).tobytes())  # length word - number of bytes in memory, extended by one 4-byte word
    f.write(np.int32(lines_input_card).tobytes())  # number of lines in input card
    f.write(input_card_bytearray)  # write input card data

    # TELESCOPE DEFINITIONS
    f.write(sync_marker)  # sync marker
    f.write(np.int32(type_tele_def).tobytes())  # type/version word
    f.write(np.int32(id_word).tobytes())  # ID word
    f.write(np.int32(len(tele_def)*16 + 4).tobytes())  # length word
    f.write(np.int32(len(tele_def)).tobytes())  # length word
    # telescope definitions written as
    # # x1 x2 ... xn y1 y2 ... yn z1 z2 ... zn r1 r2 ... rn
    for par in range(4):
        for tele in tele_def:
            f.write(np.float32(tele[par]).tobytes())

    # write 2 events TODO now manual number of events
    n_events = 2
    for evID in range(n_events):
        # EVENT HEADER
        # write the sync marker
        f.write(sync_marker)
        # type/version word
        f.write(type_event_header.to_bytes(word_size, "little"))      
        # ID word
        f.write(int(0).to_bytes(word_size, "little"))
        # length word
        f.write(np.int32(header_size_m).tobytes())
        # number of floats in header
        f.write(np.int32(header_size).tobytes())
        # write correct event number
        event_header_bytes[4:8] = np.float32(evID).tobytes()
        # write event header
        f.write(event_header_bytes)

        # ARRAY OFFSETS
        # write the sync marker
        f.write(sync_marker)
        # type/version word
        f.write(type_array_offsets.to_bytes(word_size, "little"))      
        # ID word
        f.write(int(0).to_bytes(word_size, "little"))
        # length word
        f.write(int(len(array_offsets)*12 + 4).to_bytes(word_size, "little"))
        # number of offsets
        f.write(len(array_offsets).to_bytes(word_size, "little"))
        # write array offsets as (TODO I assume?)
        # t1 t2 ... tn x1 x2 ... xn y1 y2 ... yn
        for par in range(3):
            for offset in array_offsets:          
                f.write(np.float32(offset[par]).tobytes())

        # TELESCOPE DATA
        # write the sync marker
        f.write(sync_marker)
        # type/version word
        f.write(type_tele_data.to_bytes(word_size, "little"))      
        # ID word
        f.write(int(0).to_bytes(word_size, "little"))
        # length word
        # this object contains only subobjects, so bit 30 of the length word has to be set to allow iterating over them
        n_bunches = 2
        f.write(int(24+n_bunches*16).to_bytes(3, "little"))
        f.write(int(64).to_bytes(1, "little"))

        # BUNCHES
        # not a top-level object, no sync marker
        # type/version word - version
        f.write(type_bunch.to_bytes(2, "little"))      
        f.write(int(16000).to_bytes(2, "little"))      
        # ID word
        f.write(int(0).to_bytes(word_size, "little"))
        # length word
        f.write(int(12+n_bunches*16).to_bytes(word_size, "little"))
        bunches_prefix = np.zeros(3).astype(np.float32)
        bunches_prefix_bytes = bytearray(bunches_prefix)
        bunches_prefix_bytes[4:8] = np.float32(n_bunches).tobytes()
        bunches_prefix_bytes[8:12] = (n_bunches).to_bytes(word_size, "little")
        f.write(bunches_prefix_bytes)

        for b in range(n_bunches):
            bunches = np.ones(8).astype(np.int16)
            bunches_bytes = bytearray(bunches)
            f.write(bunches_bytes)        
        
        # EVENT END
        # write the sync marker
        f.write(sync_marker)
        # type/version word
        f.write(type_event_end.to_bytes(word_size, "little"))      
        # ID word
        f.write(int(0).to_bytes(word_size, "little"))
        # length word
        f.write(np.int32(header_size_m).tobytes())
        # number of floats in header
        f.write(np.int32(header_size).tobytes())
        event_end_bytes = bytearray(data)
        event_end_bytes[0:4] = b"EVTE"
        event_end_bytes[4:8] = np.float32(evID).tobytes()
        f.write(event_end_bytes)

    # RUN END
    # write the sync marker
    f.write(sync_marker)
    # type/version word
    f.write(type_run_end.to_bytes(word_size, "little"))      
    # ID word
    f.write(int(0).to_bytes(word_size, "little"))
    # length word
    f.write(int(16).to_bytes(word_size, "little"))
    # number of floats in run end (always 3)
    f.write(int(3).to_bytes(word_size, "little"))
    run_end = bytearray(np.zeros(3).astype(np.float32)) 
    run_end[0:4] = b"RUNE"
    run_end[8:12] = np.float32(n_events).tobytes()
    f.write(run_end) 



print("Opening the created binary file")
with eventio.IACTFile(path) as f:
# with eventio.IACTFile("../cta/pyeventio/tests/resources/one_shower.dat") as f:
    print("   Opened successfully")

    # test run header
    print(f"   Run header:")
    print(f"      CORSIKA version : {f.header["version"]}")
    print(f"      Showers         : {f.header["n_showers"]}")
    print(f"      Energy range    : {f.header["energy_min"]} - {f.header["energy_max"]}")
    print(f"      Obs. level      : {f.header["observation_height"][0]}")

    # test input card
    input_card = f.input_card.decode("utf-8").split("\n")
    print(f"   Input card header: '{input_card[0]}'")

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

        # print(f"      Showers: {f.header["n_showers"]}")
        # print(f"      Energy range: {f.header["energy_min"]} - {f.header["energy_max"]}")
        # print(f"      Obs. level: {f.header["observation_height"][0]}")

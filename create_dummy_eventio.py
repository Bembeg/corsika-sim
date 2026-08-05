import numpy as np
import eventio
import gzip

import corsikaio

# path to create the dummy file at
path = "dummyfile.dat"

# empty array of 273 floats (eventIO block?)
run_header = np.zeros(273).astype(np.float32)
run_header[0] = np.float32(8.0) # CORSIKA version
run_header[3] = np.float32(8.0) # CORSIKA version
run_header[3] = np.float32(8.0) # CORSIKA version

# manually define values for the run header
header_version = np.float32(8.0)
header_date = np.float32(0)
header_n_obs_levels = np.float32(1)
header_obs_level = np.float32(2000)
header_ene_min = np.float32(10)
header_ene_max = np.float32(10)
header_cut_had = np.float32(0)
header_cut_muo = np.float32(0)
header_cut_ele = np.float32(0)
header_cut_pho = np.float32(0)
header_n_show = np.float32(1)

# put values into the run header - for reference, see run_header_fields in corsikaio/subblocks/run_header.py
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

data = bytearray(run_header)

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

word_size = 4
block_size = corsikaio.constants.BLOCK_SIZE_FLOATS
block_size_m = (block_size + 1) * word_size

# load input card template
with open("template_input_card.txt", "r") as input_card:
    data_input_card = input_card.readlines()
    lines_input_card = len(data_input_card)

# convert input card to eventIO strings and to a bytearray
input_card_bytearray = bytearray()
for line in data_input_card:
    # remove newline character
    line_strip = line.strip()
    # eventIO string format is 2 bytes for length + the string itself
    input_card_bytearray += len(line_strip).to_bytes(2, "little")
    input_card_bytearray += line_strip.encode()

print(f"length of input card bytearray: {len(input_card_bytearray)}")

with open(path, 'wb') as f:
    # RUN HEADER
    # write the sync marker
    f.write(sync_marker)
    # type/version word
    f.write(type_run_header.to_bytes(4, "little"))      
    # f.write(int(0).to_bytes(1, "little"))
    # f.write(int(8).to_bytes(1, "little"))      
    # ID word
    f.write(int(0).to_bytes(word_size, "little"))
    # length word
    f.write(block_size_m.to_bytes(word_size, "little"))
    # number of floats in header (always 273)
    f.write(block_size.to_bytes(word_size, "little"))
    # replace first 4 bytes with run header ID
    data[:4] = b'RUNH'
    # write run header data
    f.write(data)

    # INPUT CARD
    # write the sync marker
    f.write(sync_marker)
    # type/version word
    f.write(type_input_card.to_bytes(word_size, "little"))      
    # ID word
    f.write(int(0).to_bytes(word_size, "little"))
    # length word - number of bytes in memory, extended by one 4-byte word
    f.write((len(input_card_bytearray)+4).to_bytes(word_size, "little"))
    # number of lines in input card
    f.write(lines_input_card.to_bytes(word_size, "little"))
    # write run header data
    f.write(input_card_bytearray)

    # TELESCOPE DEFINITIONS
    # write the sync marker
    f.write(sync_marker)
    # type/version word
    f.write(type_tele_def.to_bytes(word_size, "little"))      
    # ID word
    f.write(int(0).to_bytes(word_size, "little"))
    # length word
    f.write(block_size_m.to_bytes(word_size, "little"))
    # number of floats in header (always 273)
    f.write(block_size.to_bytes(word_size, "little"))
    # replace first 4 bytes with run header ID
    data[:4] = b'RUNH'
    # write run header data
    f.write(data)
    # data[:4] = b'RUNE'
    # f.write(data)


print("SAMPLE FILE")
with eventio.IACTFile("/scratch/home/rprivara/Corsika/cta/pyeventio/tests/resources/one_shower.dat") as f:
    print("luleo")

print("MY FILE")
with eventio.IACTFile(path) as f:
    print("luleo")
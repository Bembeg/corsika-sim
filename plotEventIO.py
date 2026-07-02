import eventio
import sys

path = sys.argv[1]
print(f"reading file '{path}'")

with eventio.IACTFile(path) as f:
    # get input card object
    input_card = f.input_card.decode("utf-8").split("\n")
    # selected parameters 
    sel_params = ["CORSIKA", # header
            "RUNNR", # n_runs
            "EVTNR", # n_events
            "NSHOW", # n_showers
            "PRMPAR", # primary particle
            "ERANGE", # its energy
            "THETAP", # zenith angle
            "PHIP", # azimuth angle
            "OBSLEV", # observation level
            "ATMOFILE", # atmosphere table
            "MAGNET", # magnetic field
            "CERSIZ", # photon bunch size
            "CWAVLG" # cherenkov photon wavelength range
            ]
    
    # print selected parameters from the input card    
    print(f"\ninput card (selected params):")
    for param in sel_params:
        for line in input_card:
            # find row with the requested parameter
            if param in line:
                print(f"  {line}")

    print(f"\ntelescopes ({len(f.telescope_positions)}):")
    for t in range(len(f.telescope_positions)):
        print(f"    - telescope {t}")
        print(f"       - position : ({f.telescope_positions[t]["x"]/1e2}, {f.telescope_positions[t]["y"]/1e2}, {f.telescope_positions[t]["z"]/1e2}) (m?)")
        print(f"       - radius : {f.telescope_positions[t]["r"]/1e2} m")

    event_id = 0    
    print(f"\niterating events:")
    for event in f:
        if(event_id > 0):
            break

        # event header info
        print(f"  - event {event_id}:")
        print(f"     - energy            : {event.header["total_energy"]} GeV")
        print(f"     - momentum          : ({event.header["momentum_x"]}, {event.header["momentum_y"]}, {-event.header["momentum_minus_z"]}) GeV/c")

        print(f"     - starting height   : {event.header["starting_height"] / 1e5} km ({event.header["starting_altitude"]} g/cm2)")
        print(f"     - first interaction : {event.header["first_interaction_height"] / 1e5} km ({(event.header["starting_height"] + event.header["first_interaction_height"])/1e5} km)")
        
        # print(f"     - azimuth           : {event.header["azimuth"]} rad")
        # print(f"     - zenith            : {event.header["zenith"]} rad")
         
        # print(f"     - cherenkov range   : {event.header["cherenkov_wavelength_min"]} - {event.header["cherenkov_wavelength_max"]} nm")
        # print(f"     - bunch size        : {event.header["cherenkov_bunch_size"]}")

        print(f"     iterating cherenkov photon bunches ({len(event.photon_bunches[0])}):")

        bunch_id = 0
        for bunch in event.photon_bunches[0]:
            if (bunch_id > 0): 
                break

            print(f"        - bunch {bunch_id}")
            print(f"              - (x, y)          : ({bunch["x"]/1e2}, {bunch["y"]/1e2}) m") 
            print(f"              - (cx, cy)        : ({bunch["cx"]}, {bunch["cy"]})") 
            print(f"              - time            : {bunch["time"]} ns") 
            print(f"              - emission height : {bunch["zem"]/1e5} km") 
            print(f"              - photons         : {bunch["photons"]}") 
            print(f"              - wavelength      : {bunch["wavelength"]}") 
            
            bunch_id += 1
        
        event_id += 1



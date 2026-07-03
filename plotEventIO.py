import os
import sys
import numpy as np
from matplotlib import pyplot as plt

import eventio


debug = False

output_path = sys.argv[1]

input_paths = []
sim_names = []

print("inputs:")
for i in range(2, len(sys.argv)):
    print(f"   '{sys.argv[i]}' ... ", end="")

    # check if input file exists
    if os.path.exists(sys.argv[i]):
        print("ok")
    else:
        print("error")
        sys.exit(1)

    input_paths.append(sys.argv[i])

    # parse the simulation name - name of the last directory
    sim_name = sys.argv[i].split("/")[-2]
    sim_names.append(sim_name)

plot_path = "plots/c7/" + output_path + "/"

# make dir for plots
os.makedirs(plot_path, exist_ok=True)

# go over input files and find min and max values for histograms
edges = {"time": [], "zem": [], "first_int": []}

for sim in range(len(input_paths)):
    with eventio.IACTFile(input_paths[sim]) as f:
        for event in f:
            edges["first_int"].append((event.header["starting_height"] + event.header["first_interaction_height"]) / 1e5)

            for telescope in range(len(f.telescope_positions)):
                edges["zem"].append(min(event.photon_bunches[telescope]["zem"]))

print(edges["first_int"])
print(len(edges["first_int"]))
sys.exit(0)

# initialize global histograms
hists = {}
bins = {}
photons = {}

for sim in range(len(input_paths)):
    print(f"reading file '{input_paths[sim]}'")


    hists[sim] = {}
    bins[sim] = {}
    photons[sim] = {}

    bins[sim]["first_int"] = np.linspace(80, 120, 64+1)
    hists[sim]["first_int"] = np.zeros(len(bins[sim]["first_int"])-1)

    with eventio.IACTFile(input_paths[sim]) as f:
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
        # print(f"\ninput card (selected params):")
        # for param in sel_params:
        #     for line in input_card:
        #         # find row with the requested parameter
        #         if param in line:
        #             print(f"   {line}")

        # number of telescopes
        n_telescopes = len(f.telescope_positions)
        
        if(debug):
            print(f"   telescopes ({n_telescopes}):")

        for telescope in range(n_telescopes):
            radius = f.telescope_positions[telescope]["r"] / 1e2

            if(debug):
                print(f"      [{telescope}] position : ({f.telescope_positions[telescope]["x"] / 1e2}, {f.telescope_positions[telescope]["y"]/1e2}, {f.telescope_positions[telescope]["z"]/1e2}) (m?)")
                print(f"          radius   : {radius} m")

            # initialize telescope histograms
            bins[sim][telescope] = {}
            hists[sim][telescope] = {}
            photons[sim][telescope] = []
            bins[sim][telescope]["x"] = np.linspace(-1.1 * radius, 1.1 * radius, 64+1)
            hists[sim][telescope]["x"] = np.zeros(len(bins[sim][telescope]["x"])-1)
            bins[sim][telescope]["y"] = np.linspace(-1.1 * radius, 1.1 * radius, 64+1)
            hists[sim][telescope]["y"] = np.zeros(len(bins[sim][telescope]["y"])-1)
            hists[sim][telescope]["xy"] = np.zeros((len(bins[sim][telescope]["x"])-1, len(bins[sim][telescope]["y"])-1))
            bins[sim][telescope]["r"] = np.linspace(0, 1.1 * radius, 64+1)
            hists[sim][telescope]["r"] = np.zeros(len(bins[sim][telescope]["r"])-1)
            bins[sim][telescope]["cx"] = np.linspace(0, 1, 64+1)
            hists[sim][telescope]["cx"] = np.zeros(len(bins[sim][telescope]["cx"])-1)
            bins[sim][telescope]["cy"] = np.linspace(0, 1, 64+1)
            hists[sim][telescope]["cy"] = np.zeros(len(bins[sim][telescope]["cy"])-1)
            bins[sim][telescope]["wavelen"] = np.linspace(-1, 1200, 64+1)
            hists[sim][telescope]["wavelen"] = np.zeros(len(bins[sim][telescope]["wavelen"])-1)
            bins[sim][telescope]["zem"] = np.linspace(0, 1.5e5, 64+1)
            hists[sim][telescope]["zem"] = np.zeros(len(bins[sim][telescope]["zem"])-1)
            bins[sim][telescope]["time"] = np.linspace(-130, -100, 64+1)
            hists[sim][telescope]["time"] = np.zeros(len(bins[sim][telescope]["time"])-1)
            bins[sim][telescope]["photons"] = np.linspace(0, 20, 21)
            hists[sim][telescope]["photons"] = np.zeros(len(bins[sim][telescope]["photons"])-1)

        if(debug):
            print(f"   iterating events")

        for event in f:
            # collect first interaction altitudes
            hist, _ = np.histogram([(event.header["starting_height"] + event.header["first_interaction_height"]) / 1e5], bins=bins[sim]["first_int"])
            hists[sim]["first_int"] += hist

            for telescope in range(n_telescopes):
                # hit radius
                radius = np.sqrt(event.photon_bunches[telescope]["x"] * event.photon_bunches[telescope]["x"] + event.photon_bunches[telescope]["y"]*event.photon_bunches[telescope]["y"]) / 1e2
                
                # number of bunches
                photons[sim][telescope].append(sum(event.photon_bunches[telescope]["photons"]))

                # collect histograms for this event and add them to totals
                hist, _ = np.histogram(event.photon_bunches[telescope]["x"] / 1e2, bins=bins[sim][telescope]["x"])
                hists[sim][telescope]["x"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["y"] / 1e2, bins=bins[sim][telescope]["y"])
                hists[sim][telescope]["y"] += hist
                hist, _, _ = np.histogram2d(event.photon_bunches[telescope]["x"] / 1e2, event.photon_bunches[telescope]["y"] / 1e2, bins=(bins[sim][telescope]["x"], bins[sim][telescope]["y"]))
                hists[sim][telescope]["xy"] += hist
                hist, _ = np.histogram(radius, bins=bins[sim][telescope]["r"])
                hists[sim][telescope]["r"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["cx"], bins=bins[sim][telescope]["cx"])
                hists[sim][telescope]["cx"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["cy"], bins=bins[sim][telescope]["cy"])
                hists[sim][telescope]["cy"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["time"], bins=bins[sim][telescope]["time"])
                hists[sim][telescope]["time"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["zem"] / 1e2, bins=bins[sim][telescope]["zem"])
                hists[sim][telescope]["zem"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["wavelength"], bins=bins[sim][telescope]["wavelen"])
                hists[sim][telescope]["wavelen"] += hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["photons"], bins=bins[sim][telescope]["photons"])
                hists[sim][telescope]["photons"] += hist

        # print total number of bunches
        print(f"   total photons in telescopes:")

        for telescope in range(n_telescopes):
            print(f"      [{telescope}] : {sum(photons[sim][telescope])}")

print("making plots")

# first interaction altitude
fig, ax = plt.subplots()
for sim in range(len(sim_names)):
    ax.stairs(hists[sim]["first_int"], bins[sim]["first_int"])
ax.set_title("First interaction altitude")
ax.set_xlabel("altitude [km]")
ax.set_ylabel("showers")
fig.savefig(plot_path + "first_int.png", dpi=300)
plt.close()

for telescope in range(n_telescopes):
    # photon X position
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["x"], bins[sim][telescope]["x"])
    ax.set_title(f"Hit X positions (telescope {telescope})")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_hitX.png", dpi=300)
    plt.close()
    
    # photon Y position
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["y"], bins[sim][telescope]["y"])
    ax.set_title(f"Hit Y positions (telescope {telescope})")
    ax.set_xlabel("y [m]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_hitY.png", dpi=300)
    plt.close()
    
    # photon XY position - plots only for the first file even if more are provided
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_aspect("equal")
    X, Y = np.meshgrid(bins[0][telescope]["x"], bins[0][telescope]["y"])
    mesh = ax.pcolormesh(X, Y, hists[0][telescope]["xy"], cmap = "gist_heat_r")
    ax.set_title(f"Hit positions (telescope {telescope})")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    fig.colorbar(mesh, ax=ax, label="Photon density", pad=0.02, shrink=0.835)
    fig.savefig(plot_path + f"tele{telescope}_hitXY.png", dpi=300)
    plt.close()

    # correct the radius histograms by surface areas
    for i in range(len(hists[sim][telescope]["r"])):
        inner_rad = bins[sim][telescope]["r"][i]
        outer_rad = bins[sim][telescope]["r"][i+1]
        # print(f"inner_rad {inner_rad}, outer_rad {outer_rad}")
        outer_surf = 2 * 3.1415926 * outer_rad * outer_rad
        inner_surf = 2 * 3.1415926 * inner_rad * inner_rad
        surf = outer_surf - inner_surf
        # scale the histogram bin by the surface area
        hists[sim][telescope]["r"][i] = hists[sim][telescope]["r"][i] / surf

    # photon hit radius
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
       ax.stairs(hists[sim][telescope]["r"], bins[sim][telescope]["r"])
    ax.set_title(f"Hit radius (telescope {telescope})")
    ax.set_xlabel("r [m]")
    ax.set_ylabel("Photons / m$^2$")
    fig.savefig(plot_path + f"tele{telescope}_hitR.png", dpi=300)
    plt.close()

    # photon direction cosine with X
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["cx"], bins[sim][telescope]["cx"])
    ax.set_title(f"Hit direction X-cosine (telescope {telescope})")
    ax.set_xlabel("Hit direction X-cosine")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_hitCX.png", dpi=300)
    plt.close()

    # photon direction cosine with Y
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["cy"], bins[sim][telescope]["cy"])
    ax.set_title(f"Hit direction Y-cosine (telescope {telescope})")
    ax.set_xlabel("Hit direction Y-cosine")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_hitCY.png", dpi=300)
    plt.close()

    # photon hit time
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["time"], bins[sim][telescope]["time"])
    ax.set_title(f"Hit time (telescope {telescope})")
    ax.set_xlabel("Hit time [ns]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_time.png", dpi=300)
    plt.close()

    # photon emission height
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["zem"], bins[sim][telescope]["zem"])
    ax.set_title(f"Photon emission altitude (telescope {telescope})")
    ax.set_xlabel("Emission altitude [m]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_zem.png", dpi=300)
    plt.close()

    # photon wavelength
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["wavelen"], bins[sim][telescope]["wavelen"])
    ax.set_title(f"Photon wavelength (telescope {telescope})")
    ax.set_xlabel("Wavelength [nm]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_wavelen.png", dpi=300)
    plt.close()

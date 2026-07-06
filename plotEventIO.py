import os
import sys
import numpy as np
import matplotlib.lines as mlines
from matplotlib import pyplot as plt

import eventio


debug = True

output_path = sys.argv[1]

input_paths = []
sim_names = []

n_bins = 128

# Colors in plots
colors=("black", "firebrick", "mediumblue", "green", "goldenrod", "skyblue", "lightpink")
alt_color = "forestgreen"
alt_alpha = 0.6

# DPI value
dpi_val = 300

# alpha values for error bands
alpha_band = 0.15
alpha_edge = 0.40

# linestyles
linestyles=["solid", (0, (1, 1)), "none"]

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

# structure to collect min and max values of parameters
bounds = { "first_int": [],
 "time": {"min": [], "max": []},
 "zem": {"min": [], "max": []},
 "photons": [],
}

# go over input files and collect min and max values
for sim in range(len(input_paths)):
    with eventio.IACTFile(input_paths[sim]) as f:
        for event in f:
            bounds["first_int"].append((event.header["starting_height"] + event.header["first_interaction_height"]) / 1e5)

            for telescope in range(len(f.telescope_positions)):
                if (len(event.photon_bunches[telescope]["zem"]) > 0):
                    bounds["zem"]["min"].append(min(event.photon_bunches[telescope]["zem"]) / 1e2)
                    bounds["zem"]["max"].append(max(event.photon_bunches[telescope]["zem"]) / 1e2)
                
                if (len(event.photon_bunches[telescope]["time"]) > 0):
                    bounds["time"]["min"].append(min(event.photon_bunches[telescope]["time"]))
                    bounds["time"]["max"].append(max(event.photon_bunches[telescope]["time"]))
                
                bounds["photons"].append(sum(event.photon_bunches[telescope]["photons"]))

# determine absolute min and max values
bound_zem_min = min(bounds["zem"]["min"])
bound_zem_max = max(bounds["zem"]["max"])
bound_time_min = min(bounds["time"]["min"])
bound_time_max = max(bounds["time"]["max"])
bound_first_int_min = min(bounds["first_int"])
bound_first_int_max = max(bounds["first_int"])
bound_photons_min = min(bounds["photons"])
bound_photons_max = max(bounds["photons"])

if(debug):
    print("printing bounds:")
    print(f"   first inter. alt. [km] : {bound_first_int_min} - {bound_first_int_max}")
    print(f"         photons / shower : {bound_photons_min} - {bound_photons_max}")
    print(f"      emission_height [m] : {bound_zem_min} - {bound_zem_max}")
    print(f"                time [ns] : {bound_time_min} - {bound_time_max}")

# initialize global histograms
hists = {}
bins = {}
photons = {}

for sim in range(len(input_paths)):
    print(f"\nreading file '{input_paths[sim]}'")

    hists[sim] = {}
    bins[sim] = {}
    photons[sim] = {}

    bins[sim]["first_int"] = np.linspace(bound_first_int_min, bound_first_int_max, n_bins)
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
        if(debug):
            print(f"\ninput card (selected params):")
            for param in sel_params:
                for line in input_card:
                    # find row with the requested parameter
                    if param in line:
                        print(f"   {line}")

        # number of telescopes
        n_telescopes = len(f.telescope_positions)
        
        if(debug):
            print(f"   telescopes ({n_telescopes}):")

        for telescope in range(n_telescopes):
            radius = f.telescope_positions[telescope]["r"] / 1e2

            if(debug):
                print(f"      [{telescope}] position : ({f.telescope_positions[telescope]["x"] / 1e2}, {f.telescope_positions[telescope]["y"]/1e2}, {f.telescope_positions[telescope]["z"]/1e2}) m")
                print(f"          radius   : {radius} m")

            # initialize telescope histograms
            bins[sim][telescope] = {}
            hists[sim][telescope] = {}
            photons[sim][telescope] = []
            bins[sim][telescope]["x"] = np.linspace(-1.1 * radius, 1.1 * radius, n_bins)
            hists[sim][telescope]["x"] = np.zeros(len(bins[sim][telescope]["x"])-1)
            bins[sim][telescope]["y"] = np.linspace(-1.1 * radius, 1.1 * radius, n_bins)
            hists[sim][telescope]["y"] = np.zeros(len(bins[sim][telescope]["y"])-1)
            hists[sim][telescope]["xy"] = np.zeros((len(bins[sim][telescope]["x"])-1, len(bins[sim][telescope]["y"])-1))
            bins[sim][telescope]["r"] = np.linspace(0, 1.1 * radius, n_bins)
            hists[sim][telescope]["r"] = np.zeros(len(bins[sim][telescope]["r"])-1)
            bins[sim][telescope]["cx"] = np.linspace(0, 1, n_bins)
            hists[sim][telescope]["cx"] = np.zeros(len(bins[sim][telescope]["cx"])-1)
            bins[sim][telescope]["cy"] = np.linspace(0, 1, n_bins)
            hists[sim][telescope]["cy"] = np.zeros(len(bins[sim][telescope]["cy"])-1)
            bins[sim][telescope]["wavelen"] = np.linspace(-1, 1200, n_bins)
            hists[sim][telescope]["wavelen"] = np.zeros(len(bins[sim][telescope]["wavelen"])-1)
            bins[sim][telescope]["zem"] = np.linspace(bound_zem_min, bound_zem_max, n_bins)
            hists[sim][telescope]["zem"] = np.zeros(len(bins[sim][telescope]["zem"])-1)
            bins[sim][telescope]["time"] = np.linspace(bound_time_min, bound_time_max, n_bins)
            hists[sim][telescope]["time"] = np.zeros(len(bins[sim][telescope]["time"])-1)
            bins[sim][telescope]["bunch"] = np.linspace(-0.5, 19.5, 21)
            hists[sim][telescope]["bunch"] = np.zeros(len(bins[sim][telescope]["bunch"])-1)
            bins[sim][telescope]["photons"] = np.linspace(bound_photons_min, bound_photons_max, n_bins)
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
                
                # number of photons in this event and this telescope
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
                hist, _ = np.histogram(event.photon_bunches[telescope]["photons"], bins=bins[sim][telescope]["bunch"])
                hists[sim][telescope]["bunch"] += hist
                hist, _ = np.histogram(sum(event.photon_bunches[telescope]["photons"]), bins=bins[sim][telescope]["photons"])
                hists[sim][telescope]["photons"] += hist

        # print total number of bunches
        print(f"   total photons in telescopes:")

        for telescope in range(n_telescopes):
            print(f"      [{telescope}] : {sum(photons[sim][telescope])}")
            print(f"      [{telescope}] : {sum(hists[sim][telescope]["photons"])}")

# build a legend
legend = sim_names
if (len(legend) > 1):
    legend[0] += " (ref)"

# proxies for legend
proxies = []
for i in range(len(sim_names)):
    proxies.append(mlines.Line2D([], [], color=colors[i], marker=".", label=legend[i]))

print("making plots")

titles = ["First interaction altitude",
 "Hit X positions", "Hit Y positions",
 "Hit radius", "Hit direction X-cosine",
 "Hit direction Y-cosine", "Hit time",
 "Photon emission altitude", "Photon wavelength", "Bunch size", "Photons per shower"]

x_labels = ["$H_0$ [km]",
 "$x$ [m]", "$y$ [m]", "$r$ [m]",
 "$\\cos_x$", "$\\cos_y$", "$t$ [ns]",
 "$H_{em}$ [m]", "$\\lambda$ [nm]", "$N_{\\text{photons}}$ / bunch", "$N_{\\text{photons}}$ / shower"]

y_labels = ["Showers", "Photons", "Photons",
 "Photons / m$^2$", "Photons", "Photons",
 "Photons", "Photons", "Photons", "Bunches", "Showers"]

cols = ["first_int", "x", "y", "r",
 "cx", "cy", "time", "zem", "wavelen", "bunch", "photons"]

names = ["first_int", "hitX", "hitY",
 "hitR", "hitCX", "hitCY", "time",
 "Hem", "wavelen", "bunch", "photons"]

log_scale = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

normalize = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
# normalize = [0, 0, 0, 0, 0, 0, 0, 0, 0]

for plot in range(len(titles)):
    for telescope in range(n_telescopes):

        if(debug):
            print(f"Plotting {cols[plot]}, telescope {telescope}")

        if(cols[plot] != "first_int"):
            plot_title = f"{titles[plot]}\n(telescope {telescope})"
            plot_name = f"tele{telescope}_{names[plot]}"
        else:
            plot_title = f"{titles[plot]}"
            plot_name = names[plot]

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # set vertical gap between subplots and margins
        top = 0.96 - len(sim_names) * 0.036
        plt.subplots_adjust(hspace=0.05, top=top)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)
        ax2.axhline(1, c="black")

        # grid below points
        ax1.set_axisbelow(True)
        ax2.set_axisbelow(True)

        y_label = y_labels[plot]
        if (normalize[plot]):
            y_label += " (normalized)"

        # plot title and axis labels
        ax1.set_title(plot_title, loc="left")
        ax1.set_ylabel(y_label)
        ax2.set_xlabel(x_labels[plot])
        ax2.set_ylabel("ratio to ref.")

        # add grid
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")

        # log scale
        if(log_scale[plot]):
            ax1.set_yscale("log")

        # plot and save
        for sim in range(len(sim_names)):
            
            if(cols[plot] != "first_int"):
                plot_bins = bins[sim][telescope][cols[plot]]
                plot_hist = hists[sim][telescope][cols[plot]]
    
                # normalize distribution by integral
                if (normalize[plot]):
                    hist_integral = sum(plot_hist)
                    for bin in range(len(plot_hist)):
                        plot_hist[bin] = plot_hist[bin] / hist_integral

                plot_hist_ratio = plot_hist / hists[0][telescope][cols[plot]]

            else:
                plot_bins = bins[sim][cols[plot]]
                plot_hist = hists[sim][cols[plot]]

                # normalize distribution by integral
                if (normalize[plot]):
                    hist_integral = sum(plot_hist)
                    for bin in range(len(plot_hist)):
                        plot_hist[bin] = plot_hist[bin] / hist_integral

                plot_hist_ratio = plot_hist / hists[0][cols[plot]]




            # get bin centers
            bin_centers = []
            for i in range(len(plot_bins)-1):
                # calculate bin center
                bin_center = (plot_bins[i] + plot_bins[i+1]) / 2
                # append to list
                bin_centers.append(bin_center)

            

            ax1.plot(bin_centers, plot_hist, color=colors[sim], linestyle=linestyles[0], marker=".")
            ax2.plot(bin_centers, plot_hist_ratio, color=colors[sim], linestyle=linestyles[0], marker=".")
        ax1.legend(handles=proxies, fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))
        fig.savefig(plot_path + plot_name + ".png", dpi=dpi_val)
        plt.close()

        if (cols[plot] == "first_int"):
            break

sys.exit(0)

for telescope in range(n_telescopes):
    # photon X position
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])        
    # set vertical gap between subplots and margins
    top = 0.96 - len(sim_names) * 0.036
    plt.subplots_adjust(hspace=0.05, top=top)
    # Set x-axis ticks for subplots
    ax1.tick_params(axis='x', direction='in')
    ax2.tick_params(axis='x', direction='in', top=True)
    ax2.axhline(1, c="black")

    # grid below points
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # plot title and axis labels  
    ax1.set_title(f"Hit X positions (telescope {telescope})", loc="left")
    ax1.set_ylabel("Photons")
    ax2.set_xlabel("$x$ [m]")
    ax2.set_ylabel("ratio to ref.")

    # add grid
    ax1.grid(ls="dashed", c="0.85")
    ax2.grid(ls="dashed", c="0.85")

    # get bin centers
    bin_centers = []
    for i in range(len(bins[sim][telescope]["x"])-1):
        # calculate bin center
        bin_center = (bins[sim][telescope]["x"][i] + bins[sim][telescope]["x"][i+1]) / 2
        # append to list
        bin_centers.append(bin_center)

    for sim in range(len(input_paths)):
        ax1.plot(bin_centers, hists[sim][telescope]["x"], color=colors[sim], linestyle=linestyles[0], marker=".")
    ax1.legend(handles=proxies, fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))
    fig.savefig(plot_path + f"tele{telescope}_hitX.png", dpi=dpi_val)
    plt.close()
    
    # photon Y position
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])        
    # set vertical gap between subplots and margins
    top = 0.96 - len(sim_names) * 0.036
    plt.subplots_adjust(hspace=0.05, top=top)
    # Set x-axis ticks for subplots
    ax1.tick_params(axis='x', direction='in')
    ax2.tick_params(axis='x', direction='in', top=True)
    ax2.axhline(1, c="black")

    # grid below points
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # plot title and axis labels  
    ax1.set_title(f"Hit Y positions (telescope {telescope})", loc="left")
    ax1.set_ylabel("Photons")
    ax2.set_xlabel("$y$ [m]")
    ax2.set_ylabel("ratio to ref.")

    # add grid
    ax1.grid(ls="dashed", c="0.85")
    ax2.grid(ls="dashed", c="0.85")

    # get bin centers
    bin_centers = []
    for i in range(len(bins[sim][telescope]["y"])-1):
        # calculate bin center
        bin_center = (bins[sim][telescope]["y"][i] + bins[sim][telescope]["y"][i+1]) / 2
        # append to list
        bin_centers.append(bin_center)

    for sim in range(len(input_paths)):
        ax1.plot(bin_centers, hists[sim][telescope]["y"], color=colors[sim], linestyle=linestyles[0], marker=".")
    ax1.legend(handles=proxies, fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))
    fig.savefig(plot_path + f"tele{telescope}_hitY.png", dpi=dpi_val)
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
    fig.savefig(plot_path + f"tele{telescope}_hitXY.png", dpi=dpi_val)
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
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])        
    # set vertical gap between subplots and margins
    top = 0.96 - len(sim_names) * 0.036
    plt.subplots_adjust(hspace=0.05, top=top)
    # Set x-axis ticks for subplots
    ax1.tick_params(axis='x', direction='in')
    ax2.tick_params(axis='x', direction='in', top=True)
    ax2.axhline(1, c="black")

    # grid below points
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # plot title and axis labels  
    ax1.set_title(f"Hit radius (telescope {telescope})", loc="left")
    ax1.set_ylabel("Photons / m$^2$")
    ax2.set_xlabel("$r$ [m]")
    ax2.set_ylabel("ratio to ref.")

    # add grid
    ax1.grid(ls="dashed", c="0.85")
    ax2.grid(ls="dashed", c="0.85")

    # get bin centers
    bin_centers = []
    for i in range(len(bins[sim][telescope]["r"])-1):
        # calculate bin center
        bin_center = (bins[sim][telescope]["r"][i] + bins[sim][telescope]["r"][i+1]) / 2
        # append to list
        bin_centers.append(bin_center)

    for sim in range(len(input_paths)):
        ax1.plot(bin_centers, hists[sim][telescope]["r"], color=colors[sim], linestyle=linestyles[0], marker=".")
    ax1.legend(handles=proxies, fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))
    fig.savefig(plot_path + f"tele{telescope}_hitR.png", dpi=dpi_val)
    plt.close()

    # photon direction cosine with X
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["cx"], bins[sim][telescope]["cx"])
    ax.set_title(f"Hit direction X-cosine (telescope {telescope})")
    ax.set_xlabel("Hit direction X-cosine")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_hitCX.png", dpi=dpi_val)
    plt.close()

    # photon direction cosine with Y
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["cy"], bins[sim][telescope]["cy"])
    ax.set_title(f"Hit direction Y-cosine (telescope {telescope})")
    ax.set_xlabel("Hit direction Y-cosine")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_hitCY.png", dpi=dpi_val)
    plt.close()

    # photon hit time
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["time"], bins[sim][telescope]["time"])
    ax.set_title(f"Hit time (telescope {telescope})")
    ax.set_xlabel("Hit time [ns]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_time.png", dpi=dpi_val)
    plt.close()

    # photon emission height
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["zem"], bins[sim][telescope]["zem"])
    ax.set_title(f"Photon emission altitude (telescope {telescope})")
    ax.set_xlabel("Emission altitude [m]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_zem.png", dpi=dpi_val)
    plt.close()

    # photon wavelength
    fig, ax = plt.subplots()
    for sim in range(len(input_paths)):
        ax.stairs(hists[sim][telescope]["wavelen"], bins[sim][telescope]["wavelen"])
    ax.set_title(f"Photon wavelength (telescope {telescope})")
    ax.set_xlabel("Wavelength [nm]")
    ax.set_ylabel("Photons")
    fig.savefig(plot_path + f"tele{telescope}_wavelen.png", dpi=dpi_val)
    plt.close()

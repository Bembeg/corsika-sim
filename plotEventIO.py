import os
import sys
import numpy as np
import matplotlib.lines as mlines
from matplotlib import pyplot as plt
import yaml

import eventio


debug = False

error_bars = True

output_path = sys.argv[1]

input_paths = []
sim_names = []

input_name = "output.corsika"

n_bins = 64

# colors in plots
colors=("firebrick", "mediumblue", "black", "green", "goldenrod", "skyblue", "lightpink")
colors=("C1", "C2", "mediumblue", "green", "goldenrod", "skyblue", "lightpink")

alt_color = "forestgreen"
alt_alpha = 0.6

# DPI value
dpi_val = 300

# alpha values for error bands
alpha_band = 0.10
alpha_edge = 0.40

# linestyles
linestyles=["solid", (0, (1, 1)), "none"]

linewidth = 1.5

print("Inputs:")
for i in range(2, len(sys.argv)):
    print(f"   '{sys.argv[i] + "/" + input_name}' ... ", end="")

    # check if input file exists
    if os.path.exists(sys.argv[i] + "/" + input_name):
        print("ok")
    else:
        print("error")
        sys.exit(1)

    input_paths.append(sys.argv[i])

    # parse the simulation name - name of the last directory
    sim_name = sys.argv[i].split("/")[-1]
    sim_names.append(sim_name)

plot_path = "plots/c7/" + output_path + "/"

# make dir for plots
os.makedirs(plot_path, exist_ok=True)

# structure to collect min and max values of parameters
bounds = { "first_int": [],
 "time": {"min": [], "max": []},
 "zem": {"min": [], "max": []},
 "angx": {"min": [], "max": [], "mean": []},
 "angy": {"min": [], "max": [], "mean": []},
 "photons": [],
}

print("Calculating bounds")

# # go over input files and collect min and max values
# for sim in range(len(input_paths)):
#     with eventio.IACTFile(input_paths[sim] + "/" + input_name) as f:
#         for event in f:
#             bounds["first_int"].append(-event.header["first_interaction_height"] / 1e5)

#             for telescope in range(len(f.telescope_positions)):
#                 if len(event.photon_bunches) == 0:
#                     continue

#                 if (len(event.photon_bunches[telescope]["zem"]) > 0):
#                     bounds["zem"]["min"].append(min(event.photon_bunches[telescope]["zem"]) / 1e2)
#                     bounds["zem"]["max"].append(max(event.photon_bunches[telescope]["zem"]) / 1e2)
                
#                 if (len(event.photon_bunches[telescope]["time"]) > 0):
#                     bounds["time"]["min"].append(min(event.photon_bunches[telescope]["time"]))
#                     bounds["time"]["max"].append(max(event.photon_bunches[telescope]["time"]))
                
#                 if (len(event.photon_bunches[telescope]["cx"]) > 0):
#                     bounds["angx"]["mean"].append(np.mean(90 - np.multiply(np.acos(event.photon_bunches[telescope]["cx"]), 180/np.pi)))
#                     bounds["angy"]["mean"].append(np.mean(90 - np.multiply(np.acos(event.photon_bunches[telescope]["cy"]), 180/np.pi)))

#                 bounds["photons"].append(sum(event.photon_bunches[telescope]["photons"]))

# determine absolute min and max values
bound_zem_min = 2000
bound_zem_max = 15000
bound_time_min = -70
bound_time_max = -55
bound_first_int_min = 0
bound_first_int_max = 70
bound_photons_min = 0
bound_photons_max = 7e5

bound_angx_mean = np.mean(bounds["angx"]["mean"])
bound_angy_mean = np.mean(bounds["angy"]["mean"])
margin = 1
bound_angx_min = -2
bound_angx_max = 2
bound_angy_min = -1
bound_angy_max = 1

if(debug):
    print("Printing bounds:")
    print(f"   first inter. alt. [km] : {bound_first_int_min} - {bound_first_int_max}")
    print(f"   photons / shower       : {bound_photons_min} - {bound_photons_max}")
    print(f"   emission_height [m]    : {bound_zem_min} - {bound_zem_max}")
    print(f"   time [ns]              : {bound_time_min} - {bound_time_max}")
    print(f"   inc. angle X [deg]     : {bound_angx_min} - {bound_angx_max}")
    print(f"   inc. angle Y [deg]     : {bound_angy_min} - {bound_angy_max}")

# initialize global histograms
hists = {}
bins = {}
photons = {}

for sim in range(len(input_paths)):
    print(f"Reading file '{input_paths[sim] + "/" + input_name}'")

    hists[sim] = {}
    bins[sim] = {}
    photons[sim] = {}

    bins[sim]["first_int"] = np.linspace(bound_first_int_min, bound_first_int_max, 33)
    hists[sim]["first_int"] = np.zeros(32)

    with eventio.IACTFile(input_paths[sim] + "/" + input_name) as f:
        # number of telescopes
        n_telescopes = len(f.telescope_positions)
        n_events = int(f.header["n_showers"])

        if(debug):
            print(f"   events: {n_events}")
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
            
            bins[sim][telescope]["x"] = np.linspace(-2 * radius, 2 * radius, 4*n_bins+1)
            bins[sim][telescope]["y"] = np.linspace(-2 * radius, 2 * radius, 4*n_bins+1)
            bins[sim][telescope]["r"] = np.linspace(0, 2 * radius, 4*n_bins+1)
            bins[sim][telescope]["angx"] = np.linspace(bound_angx_min, bound_angx_max, n_bins+1)
            bins[sim][telescope]["angy"] = np.linspace(bound_angy_min, bound_angy_max, n_bins+1)
            bins[sim][telescope]["wavelen"] = np.linspace(-1, 1200, n_bins+1)
            bins[sim][telescope]["zem"] = np.linspace(bound_zem_min, bound_zem_max, n_bins+1)
            bins[sim][telescope]["time"] = np.linspace(bound_time_min, bound_time_max, 200)
            bins[sim][telescope]["photons"] = np.linspace(bound_photons_min, bound_photons_max, n_bins+1)
            hists[sim][telescope]["x_2D"] = np.zeros((n_events, 4*n_bins), dtype=np.float32)
            hists[sim][telescope]["y_2D"] = np.zeros((n_events, 4*n_bins), dtype=np.float32)
            hists[sim][telescope]["xy"] = np.zeros((4*n_bins, 4*n_bins))
            hists[sim][telescope]["r_2D"] = np.zeros((n_events, 4*n_bins), dtype=np.float32)
            hists[sim][telescope]["angx_2D"] = np.zeros((n_events, n_bins), dtype=np.float32)
            hists[sim][telescope]["angy_2D"] = np.zeros((n_events, n_bins), dtype=np.float32)
            hists[sim][telescope]["wavelen_2D"] = np.zeros((n_events, n_bins), dtype=np.float32)
            hists[sim][telescope]["zem_2D"] = np.zeros((n_events, n_bins), dtype=np.float32)
            hists[sim][telescope]["time_2D"] = np.zeros((n_events, 199), dtype=np.float32)
            hists[sim][telescope]["photons"] = np.zeros(n_bins, dtype=np.float32)

        if(debug):
            print(f"   iterating events")

        ev_id = 0
        for event in f:
            # collect first interaction altitudes
            if sim > 0:
                hist, _ = np.histogram((-event.header["first_interaction_height"] + 214700) / 1e5, bins=bins[sim]["first_int"])
            else:
                hist, _ = np.histogram(-event.header["first_interaction_height"] / 1e5, bins=bins[sim]["first_int"])
            hists[sim]["first_int"] += hist

            for telescope in range(n_telescopes):
                if len(event.photon_bunches) == 0:
                    continue

                # hit radius
                radius = np.sqrt(event.photon_bunches[telescope]["x"] * event.photon_bunches[telescope]["x"] + event.photon_bunches[telescope]["y"] * event.photon_bunches[telescope]["y"]) / 1e2
                
                # number of photons in this event and this telescope
                photons[sim][telescope].append(sum(event.photon_bunches[telescope]["photons"]))  

                # collect histograms for this event and add them to totals
                hist, _ = np.histogram(event.photon_bunches[telescope]["x"] / 1e2, bins=bins[sim][telescope]["x"])
                hists[sim][telescope]["x_2D"][ev_id, :] = hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["y"] / 1e2, bins=bins[sim][telescope]["y"])
                hists[sim][telescope]["y_2D"][ev_id, :] = hist
                hist, _, _ = np.histogram2d(event.photon_bunches[telescope]["x"] / 1e2, event.photon_bunches[telescope]["y"] / 1e2, bins=(bins[sim][telescope]["x"], bins[sim][telescope]["y"]))
                hists[sim][telescope]["xy"] += hist
                hist, _ = np.histogram(radius, bins=bins[sim][telescope]["r"])
                hists[sim][telescope]["r_2D"][ev_id, :] = hist
                hist, _ = np.histogram(90 - np.multiply(np.acos(event.photon_bunches[telescope]["cx"]), 180/np.pi), bins=bins[sim][telescope]["angx"])
                hists[sim][telescope]["angx_2D"][ev_id, :] = hist
                hist, _ = np.histogram(90 - np.multiply(np.acos(event.photon_bunches[telescope]["cy"]), 180/np.pi), bins=bins[sim][telescope]["angy"])
                hists[sim][telescope]["angy_2D"][ev_id, :] = hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["time"], bins=bins[sim][telescope]["time"])
                hists[sim][telescope]["time_2D"][ev_id, :] = hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["zem"] / 1e2, bins=bins[sim][telescope]["zem"])
                hists[sim][telescope]["zem_2D"][ev_id, :] = hist
                hist, _ = np.histogram(event.photon_bunches[telescope]["wavelength"], bins=bins[sim][telescope]["wavelen"])
                hists[sim][telescope]["wavelen_2D"][ev_id, :] = hist
                hist, _ = np.histogram(sum(event.photon_bunches[telescope]["photons"]), bins=bins[sim][telescope]["photons"])
                hists[sim][telescope]["photons"] += hist

            ev_id += 1

        # calculate bin-wise means in 2D histograms
        for telescope in range(n_telescopes):
            hists[sim][telescope]["x"] = np.mean(hists[sim][telescope]["x_2D"], axis=0)
            hists[sim][telescope]["y"] = np.mean(hists[sim][telescope]["y_2D"], axis=0)
            hists[sim][telescope]["r"] = np.mean(hists[sim][telescope]["r_2D"], axis=0)
            hists[sim][telescope]["angx"] = np.mean(hists[sim][telescope]["angx_2D"], axis=0)
            hists[sim][telescope]["angy"] = np.mean(hists[sim][telescope]["angy_2D"], axis=0)
            hists[sim][telescope]["wavelen"] = np.mean(hists[sim][telescope]["wavelen_2D"], axis=0)
            hists[sim][telescope]["zem"] = np.mean(hists[sim][telescope]["zem_2D"], axis=0)
            hists[sim][telescope]["time"] = np.mean(hists[sim][telescope]["time_2D"], axis=0)

        # correct the radius histograms by surface areas
        for telescope in range(n_telescopes):
            for bin in range(len(hists[sim][telescope]["r"])):
                inner_rad = bins[sim][telescope]["r"][bin]
                outer_rad = bins[sim][telescope]["r"][bin+1]
                outer_surf = 2 * 3.1415926 * outer_rad * outer_rad
                inner_surf = 2 * 3.1415926 * inner_rad * inner_rad
                surf = outer_surf - inner_surf
                # scale the histogram bin by the surface area
                hists[sim][telescope]["r"][bin] = hists[sim][telescope]["r"][bin] / surf
                hists[sim][telescope]["r_2D"][:,bin] = hists[sim][telescope]["r_2D"][:,bin] / surf

        # print total number of bunches
        print(f"   total photons in telescopes:")
        for telescope in range(n_telescopes):
            print(f"      [{telescope}] : {sum(photons[sim][telescope])}")

        # CORSIKA7 would produce a run.log file
        # CORSIKA8 would produce a summary.yaml file
        c7_log = input_paths[sim] + "/run.log"
        c8_log = input_paths[sim] + "/summary.yaml"

        if (os.path.exists(c7_log)):
            # load and read log file
            with open(c7_log, "r") as log_file:
                for line in log_file:
                    if "GENERATED EVENTS" in line:
                        line_split = line.split()
                        n_events = line_split[-1]

                    if "CORSIKA IACT" in line:
                        line_split = line.split()
                        runtime_total = line_split[line_split.index("after") + 1]

        elif (os.path.exists(c8_log)):
            # load and read log file
            with open(c8_log, "r") as read_file:
                content = yaml.safe_load(read_file)
    
                runtime_total = content["runtime_raw"]
                n_events = content["showers"]
           
        runtime_shower = float(runtime_total) / int(n_events)
        print(f"   runtime stats: total = {runtime_total} s, per shower = {runtime_shower} s ({n_events} showers)") 

# build a legend
legend = sim_names
if (len(legend) > 1):
    legend[0] += " (ref)"
legend = ["CORSIKA 7", "CORSIKA 8"]

# proxies for legend
proxies = []
for i in range(len(sim_names)):
    proxies.append(mlines.Line2D([], [], color=colors[i], marker=".", label=legend[i]))

print("Making plots")

titles = ["First interaction altitude",
 "Hit X positions", "Hit Y positions",
 "Hit radius", "Photon incident angle (X)", "Hit incident angle Y", "Photon impact time",
 "Photon emission altitude", "Photon wavelength", "Photons per shower"]

x_labels = ["$H_0$ [km]",
 "$x$ [m]", "$y$ [m]", "$r$ [m]",
 "$\\theta_x$ [deg]", "$\\theta_y$ [deg]", "$t$ [ns]",
 "$H_{em}$ [m]", "$\\lambda$ [nm]", "$N_{\\text{photons}}$ / shower"]

y_labels = ["Showers", "Photons", "Photons",
 "Photons / m$^2$", "Photons", "Photons",
 "Photons", "Photons", "Photons", "Showers"]

cols = ["first_int", "x", "y", "r",
 "angx", "angy", "time", "zem", "wavelen", "photons"]

names = ["first_int", "hitX", "hitY",
 "hitR", "hitAngX", "hitAngY", "time",
 "Hem", "wavelen", "photons"]

log_scale = [0, 0, 0, 0, 1, 1, 0, 0, 0, 0]

normalize = [1, 1, 1, 1, 1, 1, 1, 1, 1, 0]

for plot in range(len(titles)):
    for telescope in range(n_telescopes):
        if(debug):
            print(f"Plotting {cols[plot]}, telescope {telescope}")

        # special treatment for first interaction histogram
        if(cols[plot] != "first_int"):
            plot_title = f"{titles[plot]}"
            if (n_telescopes > 1):
                plot_title += "\n(telescope {telescope})"
            plot_name = f"tele{telescope}_{names[plot]}"
        else:
            plot_title = f"{titles[plot]}"
            plot_name = names[plot]

        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # set vertical gap between subplots and margins
        top = 0.96 - len(sim_names) * 0.036
        if (len(sim_names) == 1):
            top -= 0.036
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
        # ax2.set_ylabel("ratio to ref.")
        ax2.set_ylabel("C8 / C7")

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
                
                # TODO error estimation for photon histogram - for now poisson error
                if(cols[plot] == "photons"):
                    plot_errors_lo = plot_hist - np.sqrt(plot_hist)
                    plot_errors_hi = plot_hist + np.sqrt(plot_hist)
                else:
                    # for other histograms, error as SEM
                    sem = np.std(hists[sim][telescope][cols[plot] + "_2D"], axis=0, ddof=1) / np.sqrt(n_events)
                    plot_errors_lo = plot_hist - sem
                    plot_errors_hi = plot_hist + sem

                # normalize distribution by integral
                if (normalize[plot]):
                    hist_integral = sum(plot_hist)
                    for bin in range(len(plot_hist)):
                        plot_hist[bin] = plot_hist[bin] / hist_integral
                        plot_errors_lo[bin] = plot_errors_lo[bin] / hist_integral
                        plot_errors_hi[bin] = plot_errors_hi[bin] / hist_integral

                # calculate ratio to reference
                plot_hist_ratio = plot_hist / hists[0][telescope][cols[plot]]
            else:
                # special treatment for first interaction histograms
                plot_bins = bins[sim][cols[plot]]
                plot_hist = hists[sim][cols[plot]]

                # poisson error
                plot_errors_lo = plot_hist - np.sqrt(plot_hist)
                plot_errors_hi = plot_hist + np.sqrt(plot_hist)

                # normalize distribution by integral
                if (normalize[plot]):
                    hist_integral = sum(plot_hist)
                    for bin in range(len(plot_hist)):
                        plot_hist[bin] = plot_hist[bin] / hist_integral
                        plot_errors_lo[bin] = plot_errors_lo[bin] / hist_integral
                        plot_errors_hi[bin] = plot_errors_hi[bin] / hist_integral

                # calculate ratio to reference
                plot_hist_ratio = plot_hist / hists[0][cols[plot]]

            # get bin centers
            bin_centers = []
            for i in range(len(plot_bins)-1):
                # calculate bin center
                bin_center = (plot_bins[i] + plot_bins[i+1]) / 2
                # append to list
                bin_centers.append(bin_center)
     
            # plot histograms
            ax1.plot(bin_centers, plot_hist, color=colors[sim], linestyle=linestyles[0], linewidth=linewidth, marker=".")
            if error_bars:
                ax1.fill_between(bin_centers, plot_errors_lo, plot_errors_hi, linewidth=linewidth, color=(colors[sim], alpha_band), edgecolor=(colors[sim], alpha_edge), label=None)
            ax2.plot(bin_centers, plot_hist_ratio, color=colors[sim], linewidth=linewidth, linestyle=linestyles[0], marker=".")
    
            # for photon distribution plot, print total numbers
            if (cols[plot] == "photons"):
                # Annotate gaussian mean
                plt.text(0.98, 0.93 - sim*0.08, "{:.4E}".format(sum(photons[sim][telescope])), horizontalalignment='right',verticalalignment='center', transform=ax1.transAxes, color=colors[sim])

        # ratio plot y-axis range
        if (cols[plot] == "zem"):
            ax2.set_ylim(0.6, 1.4)
        if (cols[plot] == "angx"):
            ax2.set_ylim(0.6, 1.4)
        if (cols[plot] == "time"):
            ax2.set_ylim(0.0, 4)
      
        # plot legend
        # ax1.legend(handles=proxies, loc="lower right", bbox_to_anchor=(1.012, 1))
        ax1.legend(handles=proxies, loc="lower right", bbox_to_anchor=(1.015, 1), ncols=2)
        fig.savefig(plot_path + plot_name + ".png", dpi=dpi_val)
        plt.close()

        if (cols[plot] == "first_int"):
            break

# Plot photon XY positions - only if a single input file is provided 
if(len(sim_names) == 1):
    for telescope in range(n_telescopes):
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

print("Plots done\n")
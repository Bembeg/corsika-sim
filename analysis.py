#!/usr/bin/python3
# Script for analysis of Corsika8 outputs

import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.lines as mlines
from matplotlib import pyplot as plt


def print_usage():
    print("Usage: python3 analysis.py [plot-dir] [sim-names]")
    print("Example: python3 analysis.py pdg22 pdg22_E100 pdg22_E1000")

# lower quartile
def q25(x):
    return x.quantile(0.25)

# upper quartile
def q75(x):
    return x.quantile(0.75)

def energyloss():
    print("1) Running energy loss analysis")

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
    # Set vertical gap between subplots
    plt.subplots_adjust(hspace=0.05)
    # Set x-axis ticks for subplots
    ax1.tick_params(axis='x', direction='in')
    ax2.tick_params(axis='x', direction='in', top=True)

    # grid below points
    ax1.set_axisbelow(True)
    ax2.set_axisbelow(True)

    # draw lines for atmosphere layer boundaries
    if(mark_altitudes):
        for alt, thick in atmo_layers.items():
            # ax1.plot([thick, thick], [ymin, ymax*1.05], color=alt_color, ls="dashed", lw=1)
            ax2.plot([thick, thick], [ratio_range[0], ratio_range[1]], color=(alt_color, alt_alpha), ls="dashed", lw=1)
            text = str("{:.1f}".format(alt/1000))
            ax2.text(thick-10, ratio_range[0] - (ratio_range[1]-ratio_range[0])*0.29, text, color=alt_color)
        ax2.text(0.32, -0.44, "$H$ [km]", transform=ax2.transAxes, color=alt_color)

    # horizontal line at 1
    ax2.axhline(1, c="black")

    # Dictionary for dataframes
    res = {}

    # Mark first run as reference, used for ratio plots
    ref = sim_dir[0]

    # Iterate over runs
    for path in sim_dir:
        # Parse run name
        name = path.split("/")[1]
        # Get index of this run
        id = sim_dir.index(path)
        # If this run is ref, add that to its name
        if (id == 0 and len(sim_dir) > 1): name += " (ref)"
        # Get color
        color = colors[id]

        # Calculate means and SEMs for columns
        res[path] = data[path]["energyloss"].groupby("X").agg({"total":["median", q25, q75]})
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

        # Calculate errors and ratio vs reference
        res[path]["errH"] = res[path]["total_q75"] - res[path]["total_median"]
        res[path]["errL"] = res[path]["total_median"] - res[path]["total_q25"]
        res[path]["ratio"] = res[path]["total_median"] / res[ref]["total_median"]
        res[path]["ratio_errH"] = res[path]["ratio"] + res[path]["ratio"] * np.sqrt( np.square(res[path]["errH"] / res[path]["total_median"]) + np.square(res[ref]["errH"] / res[ref]["total_median"]))
        res[path]["ratio_errL"] = res[path]["ratio"] - res[path]["ratio"] * np.sqrt( np.square(res[path]["errL"] / res[path]["total_median"]) + np.square(res[ref]["errL"] / res[ref]["total_median"]))

        # get relevant selection of data
        sel = res[path][res[path]["X"] < X_limit]

        # Plot main subplot
        sel.plot(x="X", y="total_median",
                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="$E_{loss}$ [GeV]", marker=".",
                ax=ax1, legend=True, label=name, color=color, linestyle=linestyles[0])

        # draw error band around points
        ax1.fill_between(x=sel["X"], y1=sel["total_q25"], y2=sel["total_q75"],
            color=(color, alpha_band), edgecolor=(color, alpha_edge))

        # Plot ratio subplot
        if path != ref:
            sel.plot(x="X", y="ratio", grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="ratio to ref.",
                marker=".", ax=ax2, legend=False, label=name, color=color, linestyle=linestyles[0])

            # draw error band around points
            if (plot_ratio_errors):
                ax2.fill_between(sel["X"], sel["ratio_errL"], sel["ratio_errH"],
                color=(color, alpha_band), edgecolor=(color, alpha_edge))

    # get current main plot y-axis range
    ymin, ymax = ax1.get_ylim()

    # draw lines for atmosphere layer boundaries
    if (mark_altitudes):
        for alt, thick in atmo_layers.items():
            ax1.plot([thick, thick], [ymin, ymax*1.05], color=(alt_color, alt_alpha), ls="dashed", lw=1)

    # grid and axes
    ax1.grid(ls="dashed", c="0.85")
    ax2.grid(ls="dashed", c="0.85")
    ax2.set_ylim(ratio_range)
    ax1.set_ylim(ymin, ymax)
    ax1.set_title("Median energy loss", loc="left")
    ax2.xaxis.set_label_coords(0.55, -0.32)

    # Legend fontsize and position
    ax1.legend(fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))

    # Plot and save
    plot_path = plot_dir + "eloss.png"
    fig.savefig(plot_path, dpi=dpi_val)
    print("  - generated plot '", plot_path + "'", sep="")


def interactions():
    print("2) Running interactions analysis")

def production():
    print("3) Running production analysis")

    # Define which columns to plot and corresponding labels, titles and tags
    cols = ["muon", "hadron"]
    label = [r"$N_{\mu^{\pm}}", r"$N_{hadr.}"]
    title = [r"$\mu^{\pm}$", "hadrons"]
    tag = ["muon", "hadron"]

    # Dictionary for dataframes
    res = {}

    # Mark first run as reference, used for ratio plots
    ref = sim_dir[0]

    # Iterate over runs and calculate means and SEMs for columns
    for path in sim_dir:
        res[path] = data[path]["production_profile"].groupby("X").agg(["mean", "sem"])
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

        # Calculate ratio vs reference
        for col in cols:
            res[path][col + "_ratio"] = res[path][col + "_mean"] / res[ref][col + "_mean"]
            res[path][col + "_ratio_err"] = res[path][col + "_ratio"] * np.sqrt( np.square(res[path][col + "_sem"] / res[path][col + "_mean"]) + np.square(res[ref][col + "_sem"] / res[ref][col + "_mean"]) )

    # Iterate over plots
    for n in range(len(cols)):
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # Set vertical gap between subplots
        plt.subplots_adjust(hspace=0.05)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)
        ax2.axhline(1, c="black")

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Parse run name
            name = path.split("/")[1]
            # Get index of this run
            id = sim_dir.index(path)
            # If this run is ref, add that to its name
            if (id == 0 and len(sim_dir)>1): name += " (ref)"
            # Get color
            color = colors[id]

            # Plot main subplot
            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_mean", yerr=cols[n] + "_sem", title="Avg. number of " + title[n] + " produced per shower",
                                                    grid=True, xlabel="$X$ [g/cm$^2$]", ylabel=label[n] + "^{prod}$", marker=".",
                                                    ax=ax1, legend=True, label=name, color=color)
            # Plot ratio subplot
            if (path != ref):
                res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_ratio", yerr=cols[n] + "_ratio_err",
                                                    grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="ratio vs ref.", marker=".",
                                                    ax=ax2, legend=False, label=name, color=color)
        # Add grid
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")
        ax2.set_ylim(ratio_range)

        # Plot and save
        plot_path = plot_dir + "prod_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=dpi_val)
        print("  - generated plot '", plot_path + "'", sep="")

def profile():
    print ("4) Running longitudinal profile analysis")

    # Define which columns to plot and corresponding labels, titles and tags
    cols = ["ep", "muon", "photon", "hadron"]
    label = [r"$N_{e^{\pm}}$", r"$N_{\mu^{\pm}}$", r"$N_{\gamma}$", r"$N_{hadr.}$"]
    title = [r"$e^{\pm}$", r"$\mu^{\pm}$", "photons", "hadrons"]
    tag = ["ep", "muon", "photon", "hadron"]

    # Dictionary for dataframes
    res = {}

    # Mark first run as reference, used for ratio plots
    ref = sim_dir[0]

    # Iterate over runs and calculate means and SEMs for columns
    for path in sim_dir:
        # Add values for positive and negative particles
        data[path]["profile"]["muon"] = data[path]["profile"]["muplus"] + data[path]["profile"]["muminus"]
        data[path]["profile"]["ep"] = data[path]["profile"]["electron"] + data[path]["profile"]["positron"]

        # Calculate means and SEMs for columns
        res[path] = data[path]["profile"].groupby("X").agg(["median", q25, q75])
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

        # Calculate errors and ratio vs reference
        for col in cols:
            res[path][col + "_errL"] = res[path][col + "_median"] - res[path][col + "_q25"]
            res[path][col + "_errH"] = res[path][col + "_q75"] - res[path][col + "_median"]
            res[path][col + "_ratio"] = res[path][col + "_median"] / res[ref][col + "_median"]
            res[path][col + "_ratio_errL"] = res[path][col + "_ratio"] - res[path][col + "_ratio"] \
                * np.sqrt( np.square(res[path][col + "_errL"] / res[path][col + "_median"]) \
                + np.square(res[ref][col + "_errL"] / res[ref][col + "_median"]) )
            res[path][col + "_ratio_errH"] = res[path][col + "_ratio"] + res[path][col + "_ratio"] \
                * np.sqrt( np.square(res[path][col + "_errH"] / res[path][col + "_median"]) \
                + np.square(res[ref][col + "_errH"] / res[ref][col + "_median"]) )

    # Iterate over plots
    for n in range(len(cols)):
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # Set vertical gap between subplots
        plt.subplots_adjust(hspace=0.05)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)
        
        # draw lines for atmosphere layer boundaries
        if(mark_altitudes):
            for alt, thick in atmo_layers.items():
                # ax1.plot([thick, thick], [ymin, ymax*1.05], color=alt_color, ls="dashed", lw=1)
                ax2.plot([thick, thick], [ratio_range[0], ratio_range[1]], color=(alt_color, alt_alpha), ls="dashed", lw=1)
                text = str("{:.1f}".format(alt/1000))
                ax2.text(thick-10, ratio_range[0] - (ratio_range[1]-ratio_range[0])*0.29, text, color=alt_color)
            ax2.text(0.32, -0.44, "$H$ [km]", transform=ax2.transAxes, color=alt_color)

        # horizontal line at 1
        ax2.axhline(1, c="black")

        # grid below points
        ax1.set_axisbelow(True)
        ax2.set_axisbelow(True)

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Parse run name
            name = path.split("/")[1]
            # Get index of this run
            id = sim_dir.index(path)
            # If this run is ref, add that to its name
            if (id == 0 and len(sim_dir)>1): name += " (ref)"
            # Get color
            color = colors[id]

            # get relevant selection of data
            sel = res[path][res[path]["X"] < X_limit]

            # Plot main subplot
            sel.plot(x="X", y=cols[n] + "_median",
                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel=label[n], marker=".",
                ax=ax1, legend=True, label=name, color=color)

            # draw error band around points
            ax1.fill_between(x=sel["X"], y1=sel[cols[n] + "_q25"], y2=sel[cols[n] + "_q75"],
                color=(color, alpha_band), edgecolor=(color, alpha_edge))

            # Plot ratio subplot
            if (path != ref):
                sel.plot(x="X", y=cols[n] + "_ratio", grid=True, xlabel="$X$ [g/cm$^2$]",
                ylabel="ratio to ref.", marker=".", ax=ax2, legend=False, label=name, color=color)

                # draw error band around points
                if (plot_ratio_errors):
                    ax2.fill_between(sel["X"], sel[cols[n] + "_ratio_errL"], sel[cols[n] + "_ratio_errH"],
                    color=(color, alpha_band), edgecolor=(color, alpha_edge))

        # get current main plot y-axis range
        ymin, ymax = ax1.get_ylim()

        # draw lines for atmosphere layer boundaries
        if(mark_altitudes):
            for alt, thick in atmo_layers.items():
                ax1.plot([thick, thick], [ymin, ymax*1.05], color=(alt_color, alt_alpha), ls="dashed", lw=1)

        # grid and axes
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")
        ax1.set_ylim(ymin, ymax)
        ax2.set_ylim(ratio_range)
        ax1.set_title("Median longitudinal\nprofile - " + title[n], loc="left")
        ax2.xaxis.set_label_coords(0.55, -0.32)

        # Legend fontsize
        ax1.legend(fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))

        # Plot and save
        plot_path = plot_dir + "profile_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=dpi_val)
        print("  - generated plot '", plot_path + "'", sep="")

def observation():
    print("5) Running observation plane analysis")

    # Define which columns to plot and corresponding labels, titles and tags
    pdg=[11, 13, 22]
    cols = ["ep", "muon", "photon"]
    title = [r"$e^{\pm}$", r"$\mu^{\pm}$", "photons"]
    tag = ["ep", "muon", "photon"]

    # Dictionary for dataframes
    res = {}

    # Mark first run as reference, used for ratio plots
    ref = sim_dir[0]

    # dictionaries for median and IQR histograms
    R_medians = {}
    R_25pers = {}
    R_75pers = {}
    T_medians = {}
    T_25pers = {}
    T_75pers = {}

    # Iterate over sims
    for path in sim_dir:
        # Calculate R from (x,y)
        data[path]["particles"]["R"] = pow(pow(data[path]["particles"]["x"],2) + pow(data[path]["particles"]["y"],2), 0.5)

        res[path] = data[path]["particles"]

        # get number of runs (=showers)
        n_runs = int(res[path].max()["shower"] + 1)

        # add empty dictionaries for this sim
        R_medians[path] = {}
        R_25pers[path] = {}
        R_75pers[path] = {}
        T_medians[path] = {}
        T_25pers[path] = {}
        T_75pers[path] = {}

        # process for particle types
        for p in range(len(cols)):
            # filter dataframe for particle type
            filt_part = res[path][abs(res[path]["pdg"]) == pdg[p]]

            # get minima and maxima for histogram binning from reference data
            if (path == ref):
                R_min = 0
                R_max = filt_part["R"].quantile(0.99)
                T_min = filt_part["kinetic_energy"].quantile(0.0001)
                T_max = filt_part["kinetic_energy"].quantile(0.999)

                # histogram binning
                R_bins = np.linspace(R_min, R_max, n_bins+1)
                T_bins = np.logspace(np.log10(T_min), np.log10(T_max), n_bins+1)

            # prepare median and IQR histograms
            R_meds = np.zeros(n_bins)
            R_75p = np.zeros(n_bins)
            R_25p = np.zeros(n_bins)
            T_meds = np.zeros(n_bins)
            T_75p = np.zeros(n_bins)
            T_25p = np.zeros(n_bins)

            # arrays for histograms from individual runs
            R_hists = []
            T_hists = []

            # collect histograms from individual runs
            for r in range(n_runs):
                # filter dataframe for each run
                filt_run = filt_part[filt_part["shower"] == r]

                # get histogram of R and kinetic energy
                R_hist, _ = np.histogram(filt_run["R"], R_bins)
                T_hist, _ = np.histogram(filt_run["kinetic_energy"], T_bins)

                # store histograms
                R_hists.append(R_hist)
                T_hists.append(T_hist)

            # process histograms and get median values
            for b in range(n_bins):
                # arrays for values in this bin
                R_val = []
                T_val = []

                # iterate over all runs
                for r in range(n_runs):
                    # append values
                    R_val.append(R_hists[r][b])
                    T_val.append(T_hists[r][b])

                # calculate median and interquartile range
                R_median = np.median(R_val)
                R_25per = np.quantile(R_val, 0.25)
                R_75per = np.quantile(R_val, 0.75)
                T_median = np.median(T_val)
                T_25per = np.quantile(T_val, 0.25)
                T_75per = np.quantile(T_val, 0.75)

                # fill median and IQR into the proper bin
                R_meds[b] = R_median
                R_75p[b] = R_75per
                R_25p[b] = R_25per
                T_meds[b] = T_median
                T_75p[b] = T_75per
                T_25p[b] = T_25per

            # store histograms in the main arrays
            R_medians[path][p] = R_meds
            R_75pers[path][p] = R_75p
            R_25pers[path][p] = R_25p
            T_medians[path][p] = T_meds
            T_75pers[path][p] = T_75p
            T_25pers[path][p] = T_25p

    # Plotting of radius
    for n in range(len(cols)):
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # Set vertical gap between subplots
        plt.subplots_adjust(hspace=0.05)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)
        ax2.axhline(1, c="black")

        # grid below points
        ax1.set_axisbelow(True)
        ax2.set_axisbelow(True)

        # get bin centers
        bin_centers = []
        for i in range(n_bins):
            # calculate bin center
            bin_center = (R_bins[i] + R_bins[i+1]) / 2
            # append to list
            bin_centers.append(bin_center)

        # histogram of reference values and errors (IQR)
        ref_hist = R_medians[ref][n]
        ref_errL = R_medians[ref][n] - R_25pers[ref][n]
        ref_errH = R_75pers[ref][n] - R_medians[ref][n]

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Get index of this run
            id = sim_dir.index(path)
            # Get color
            color = colors[id]

            # histogram of values and errors
            hist = R_medians[path][n]
            errL = R_medians[path][n] - R_25pers[path][n]
            errH = R_75pers[path][n] - R_medians[path][n]

            # plot points
            ax1.plot(bin_centers, hist, color=color, linestyle=linestyles[0], marker=".")
            # plot error bands
            ax1.fill_between(bin_centers, R_25pers[path][n], R_75pers[path][n], color=(color, alpha_band), edgecolor=(color, alpha_edge), label=None)

            # plot ratio vs reference
            if (path != ref):
                # calculate ratio and errors
                ratio = hist / ref_hist
                ratio_errL = ratio - ratio * np.sqrt(np.square(ref_errL / ref_hist) + np.square(errL / hist))
                ratio_errH = ratio + ratio * np.sqrt(np.square(ref_errH / ref_hist) + np.square(errH / hist))

                # plot ratio points
                ax2.plot(bin_centers, ratio, color=color, marker=".", linestyle=linestyles[0], label=None)
                # plot error bands
                ax2.fill_between(bin_centers, ratio_errL, ratio_errH, color=(color, alpha_band), edgecolor=(color, alpha_edge), label=None)

        # logscale
        ax1.set_yscale("log")

        # plot title and axis labels
        ax1.set_title("Hit radius on\nground - " + title[n], loc="left")
        ax1.set_ylabel("$N$")
        ax2.set_xlabel("$R$ [m]")
        ax2.set_ylabel("ratio to ref.")

        # Add grid
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")
        ax2.set_ylim(ratio_range_large)

        # legend entries
        legend = [name.split("/")[1] for name in sim_dir]
        if (len(legend) > 1):
            legend[0] += " (ref)"

        # proxies for legend
        proxies = []
        for i in range(len(sim_dir)):
            proxies.append(mlines.Line2D([], [], color=colors[i], marker=".", label=legend[i]))

        ax1.legend(handles=proxies, fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))

        # Plot and save
        plot_path = plot_dir + "ground_R_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=dpi_val)
        print("  - generated plot '", plot_path + "'", sep="")

    # Plotting of kinetic energy
    for n in range(len(cols)):
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # Set vertical gap between subplots
        plt.subplots_adjust(hspace=0.05)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)
        ax2.axhline(1, c="black")

        # grid below points
        ax1.set_axisbelow(True)
        ax2.set_axisbelow(True)

        # get bin centers
        bin_centers = []
        for i in range(n_bins):
            # calculate bin center
            bin_center = pow(10,(np.log10(T_bins[i]) + np.log10(T_bins[i+1])) / 2)
            # append to list
            bin_centers.append(bin_center)

        # histogram of reference values and errors (IQR)
        ref_hist = T_medians[ref][n]
        ref_errL = T_medians[ref][n] - T_25pers[ref][n]
        ref_errH = T_75pers[ref][n] - T_medians[ref][n]

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Get index of this run
            id = sim_dir.index(path)
            # Get color
            color = colors[id]

            # histogram of values and errors
            hist = T_medians[path][n]
            errL = T_medians[path][n] - T_25pers[path][n]
            errH = T_75pers[path][n] - T_medians[path][n]

            # plot points
            ax1.plot(bin_centers, hist, color=color, linestyle=linestyles[0], marker=".")
            # plot error bands
            ax1.fill_between(bin_centers, T_25pers[path][n], T_75pers[path][n], color=(color, alpha_band), edgecolor=(color, alpha_edge), label=None)

            # plot ratio vs reference
            if (path != ref):
                # calculate ratio and errors
                ratio = hist / ref_hist
                ratio_errL = ratio - ratio * np.sqrt(np.square(ref_errL / ref_hist) + np.square(errL / hist))
                ratio_errH = ratio + ratio * np.sqrt(np.square(ref_errH / ref_hist) + np.square(errH / hist))

                # plot ratio points
                ax2.plot(bin_centers, ratio, color=color, marker=".", linestyle=linestyles[0], label=None)
                # plot error bands
                ax2.fill_between(bin_centers, ratio_errL, ratio_errH, color=(color, alpha_band), edgecolor=(color, alpha_edge), label=None)

        # logscale
        ax1.set_xscale("log")
        ax1.set_yscale("log")

        # plot title and axis labels
        ax1.set_title("Kinetic energy\non ground - " + title[n], loc="left")
        ax1.set_ylabel("$N$")
        ax2.set_xlabel("$T$ [GeV]")
        ax2.set_ylabel("ratio to ref.")

        # Add grid
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")
        ax2.set_ylim(ratio_range_large)

        # legend entries
        legend = [name.split("/")[1] for name in sim_dir]
        if (len(legend) > 1):
            legend[0] += " (ref)"

        # proxies for legend
        proxies = []
        for i in range(len(sim_dir)):
            proxies.append(mlines.Line2D([], [], color=colors[i], marker=".", label=legend[i]))

        ax1.legend(handles=proxies, fontsize="small", loc="lower right", bbox_to_anchor=(1.012, 1))

        # Plot and save
        plot_path = plot_dir + "ground_Ekin_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=dpi_val)
        print("  - generated plot '", plot_path + "'", sep="")

def runtimes():
    print("6) Running runtime analysis")

    # Dictionary for dataframes
    res = {}

    # Mark first run as reference, used for ratio plots
    ref = sim_dir[0]

    # Iterate over runs
    for path in sim_dir:
        res[path] = data[path]["runtime"]

        res[path]["rt_per_sh"] = res[path]["runtime"] / res[path]["showers"]
        res[path]["rt_diff"] = res[path]["rt_per_sh"] / res[ref]["rt_per_sh"]

    # Create figure
    fig, ax = plt.subplots()

    # Iterate over runs and generate plots
    for path in sim_dir:
        # Get index of this run
        id = sim_dir.index(path)
        # Get color
        color = colors[id]

        # Plot
        data[path]["runtime"].hist(column="rt_per_sh", ax=ax, bins=24, color=color, log=False, histtype="step")

    # Add grid
    ax.grid(ls="dashed", c="0.85")

    # Set title and axis labels
    plt.title("Runtime per shower")
    plt.xlabel("Runtime [s]")
    plt.ylabel("$N$")

    # Set legend
    legend = [name.split("/")[1] for name in sim_dir]
    if (len(legend) > 1):
        legend[0] += " (ref)"
    plt.legend(legend)

    # More y-axis range to make room for the legend
    ax.set_ylim(ax.get_ylim()[0], 1.2*ax.get_ylim()[1])

    # Current axis ranges
    (ymin, ymax) = ax.get_ylim()
    (xmin, xmax) = ax.get_xlim()

    # Starting y-position for annotations of gaussian means
    y_label = (ymax-ymin)*0.04

    # Iterate over runs and fit histograms
    for path in sim_dir:
        # Get index of this run
        id = sim_dir.index(path)
        # Get color
        color = colors[id]

        # Fit with gaussian
        (mu, sigma) = norm.fit(data[path]["runtime"]["rt_per_sh"])
        print("  - ", path.split("/")[1], " : mu=", "{:.4f}".format(mu),", sigma=", "{:.4f}".format(sigma), sep="")

        # Draw vertical line at gaussian mean
        plt.axvline(mu, ls="dashed", c=color, label="", lw=1)

        # Annotate gaussian mean
        plt.text(mu + (xmax-xmin)*0.007, 0 + y_label, str("{:.2f}".format(mu)), bbox=dict(boxstyle='square,pad=0.15',
            color=("white",0.9)), color=color)

        # Push y-position for gaussian mean annotations
        y_label += (ymax-ymin)*0.06

    # Plot and save
    plot_path = plot_dir + "runtimes.png"
    fig.savefig(plot_path, dpi=dpi_val)
    print("  - generated plot '", plot_path + "'", sep="")

    # Create figure
    fig, ax = plt.subplots()
    ax.axvline(1, c="black")

    # Iterate over runs and generate plots
    for path in sim_dir:
        # Get index of this run
        id = sim_dir.index(path)
        # Get color
        color = colors[id]

        # Plot
        if (path != ref):
            data[path]["runtime"].hist(column="rt_diff", ax=ax, bins=16, color=color, log=False, histtype="step")

    # Add grid
    ax.grid(ls="dashed", c="0.85")

    # Set title and axis labels
    plt.title("Runtime difference for same seed")
    plt.xlabel(r"$\frac{Runtime~(interp. atmo)}{Runtime~(expon. atmo)}$")
    plt.ylabel("$N$")

    # Plot and save
    plot_path = plot_dir + "runtimes_seed.png"
    fig.savefig(plot_path, dpi=dpi_val)
    print("  - generated plot '", plot_path + "'", sep="")

# Check if any arguments were passed
if len(sys.argv) == 1:
    print("No simulation name(s) passed")
    print_usage()
    exit(1)

# altitudes of atmosphere layer boundaries
atmo_layers = {0: 0, 7e3: 0, 11.4e3: 0, 37e3: 0}

# Limit max X in plots
X_limit = 1030

# DPI value
dpi_val = 300

# alpha values for error bands
alpha_band = 0.15
alpha_edge = 0.40

# linestyles
linestyles=["solid", (0, (1, 1)), "none"]

# plot error bands in ratio plots
plot_ratio_errors = True

# cap size for errorbars
err_capsize = 2

# ratio subplot y-axis range
ratio_range = [0.85, 1.15]
ratio_range_large = [0, 3]

# histogram bins
n_bins = 64

# Map modules and output files inside
output_types = {"energyloss": "dEdX",
                "interactions": "interactions",
                "particles": "particles",
                "production_profile": "profile",
                "profile": "profile"}

# Colors in plots
colors=("firebrick", "mediumblue", "green", "goldenrod")
alt_color = "forestgreen"
alt_alpha = 0.6

# mark altitudes in addition to grammage
mark_altitudes = False

# ---- END OF INPUT ----

# Plot directory
plot_dir = "plots/out/" + sys.argv[1] + "/"
os.makedirs(plot_dir, exist_ok=True)

# Declare dictionaries to hold dataframes
data = {}

print("Passed ", len(sys.argv)-2, " argument(s), verifying run validity:", sep="")

# Check whether run directories are valid
sim_dir = []
for sim_name in sys.argv[2:]:
    print("  -", sim_name, end=": ")

    # Check zenith angle
    if "_z0_" not in sim_name:
        # print("Not vertical shower, disabling altitude marks")
        mark_altitudes = False

    # Check if merged directory exists
    path = "output/" + sim_name + "/merged/"
    if os.path.exists(path):
        sim_dir.append(path)
        data[path] = {}
        print("OK - merged directory found, path: '", path, "'", sep="")
        continue

    # If no merged dir, check if corsika output directories exist
    path = "output/" + sim_name + "/"
    if os.path.exists(path + "summary.yaml"):
        sim_dir.append(path)
        data[path] = {}
        print("OK - output directories found, path: '", path, "'", sep="")
        continue

    print("ERR - invalid name (no merged or direct output)")
    exit(1)

print("Found", len(sim_dir), "valid runs, loading data")

# Iterate over output directories and files
for path in sim_dir:
    # print("  - processing run '", path, "'", sep="")

    for mod, file in output_types.items():
        # print("   - processing module '", mod, "' (file '", path+mod+"/"+file, ".parquet')", sep="")

        # Compose sim file name
        sim_file = path + mod + "/" + file + ".parquet"

        # Read from parquet file as dataframe
        data[path][mod] = pd.read_parquet(sim_file, "pyarrow")

    # Runtimes
    data[path]["runtime"] = pd.read_csv(path + "/runtimes.csv", index_col=False)

# look up altitude to grammage mapping
if (mark_altitudes):
    atmo_table = pd.read_csv("data/USStdBK_full.csv")
    for a in atmo_layers:
        thick = atmo_table[atmo_table["alt"] == a]["thick"].values[0]
        atmo_layers[a] = thick

print("Loaded data")

# Analysis
energyloss()
# interactions()
# production()
profile()
# observation()
# runtimes()

print("All done")

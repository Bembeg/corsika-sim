#!/usr/bin/python3
# Script for analysis of Corsika8 outputs

import pandas as pd
import numpy as np
import os
import sys
from matplotlib import pyplot as plt
from scipy.stats import norm


def print_usage():
    print("Usage: python3 analysis.py [sim-names]")
    print("Example: python3 analysis.py pdg22_E100 pdg22_E1000")

def energyloss():
    print("1) Running energy loss analysis")

    # Create figure
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
    # Set vertical gap between subplots
    plt.subplots_adjust(hspace=0.05)
    # Set x-axis ticks for subplots
    ax1.tick_params(axis='x', direction='in')
    ax2.tick_params(axis='x', direction='in', top=True)
    
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
        # if (id == 0 and len(sim_dir)>1): name += " (ref)"
        # Get color
        color = colors[id]

        # Calculate means and SEMs for columns
        res[path] = data[path]["energyloss"].groupby("X").agg({"total":["mean", "sem"]})
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

        # Calculate ratio vs reference
        res[path]["ratio"] = res[path]["total_mean"] / res[ref]["total_mean"]

        res[path]["ratio_err"] = res[path]["ratio"] * np.sqrt( np.square(res[path]["total_sem"] / res[path]["total_mean"]) + np.square(res[ref]["total_sem"] / res[ref]["total_mean"]) )

        # Plot main subplot
        res[path][res[path]["X"] < X_limit].plot(x="X", y="total_mean", yerr="total_sem", title="Avg. energy loss per shower",
                                                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="$E_{loss}$ [GeV]", marker=".",
                                                ax=ax1, legend=True, label=name, color=color)
    
        # Plot ratio subplot
        res[path][res[path]["X"] < X_limit].plot(x="X", y="ratio", yerr="ratio_err",
                                                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="ratio vs ref.", marker=".",
                                                ax=ax2, legend=False, label=name, color=color)

        plt.fill_between(x="X", y1="ratio - ratio_err", y2="ratio + ratio_err", alpha=0.5, label="label")

    # Add grid
    ax1.grid(ls="dashed", c="0.85")
    ax2.grid(ls="dashed", c="0.85")
    # ax2.set_ylim([0, 2])
    
    # Plot and save
    plot_path = plot_dir + "eloss.png"
    fig.savefig(plot_path, dpi=300)
    print("  - generated plot '", plot_path + "'", sep="")

def interactions():
    print("2) Running interactions analysis")

def production():
    print("3) Running production analysis")

    # Define which columns to plot and corresponding labels, titles and tags
    cols = ["electron-positron", "muon", "photon", "hadron"]
    label = [r"$N_{e^{\pm}}", r"$N_{\mu^{\pm}}", r"$N_{\gamma}", r"$N_{hadr.}"]
    title = [r"$e^{\pm}$", r"$\mu^{\pm}$", "photons", "hadrons"]
    tag = ["ep", "muon", "photon", "hadron"]

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

    # Iterate over plots
    for n in range(len(cols)):
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # Set vertical gap between subplots
        plt.subplots_adjust(hspace=0.05)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Parse run name
            name = path.split("/")[1]
            # Get index of this run
            id = sim_dir.index(path)
            # If this run is ref, add that to its name
            # if (id == 0 and len(sim_dir)>1): name += " (ref)"
            # Get color
            color = colors[id]

            # Plot main subplot
            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_mean", yerr=cols[n] + "_sem", title="Avg. number of " + title[n] + " produced per shower",
                                                    grid=True, xlabel="$X$ [g/cm$^2$]", ylabel=label[n] + "^{prod}$", marker=".",
                                                    ax=ax1, legend=True, label=name, color=color)
            # Plot ratio subplot
            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_ratio", 
                                                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="ratio vs ref.", marker=".",
                                                ax=ax2, legend=False, label=name, color=color)
        # Add grid
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")
        # ax2.set_ylim([0, 2])

        # Plot and save
        plot_path = plot_dir + "prod_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=300)
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
        res[path] = data[path]["profile"].groupby("X").agg(["mean", "sem"])
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

        # Calculate ratio vs reference
        for col in cols:
            res[path][col + "_ratio"] = res[path][col + "_mean"] / res[ref][col + "_mean"]

    # Iterate over plots
    for n in range(len(cols)):
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.7, 0.3])
        # Set vertical gap between subplots
        plt.subplots_adjust(hspace=0.05)
        # Set x-axis ticks for subplots
        ax1.tick_params(axis='x', direction='in')
        ax2.tick_params(axis='x', direction='in', top=True)

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Parse run name
            name = path.split("/")[1]
            # Get index of this run
            id = sim_dir.index(path)
            # If this run is ref, add that to its name
            # if (id == 0 and len(sim_dir)>1): name += " (ref)"
            # Get color
            color = colors[id]

            # Plot main subplot
            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_mean", yerr=cols[n] + "_sem", title="Longitudinal profile - " + title[n],
                                                    grid=True, xlabel="$X$ [g/cm$^2$]", ylabel=label[n], marker=".",
                                                    ax=ax1, legend=True, label=name, color=color)

            # Plot ratio subplot
            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_ratio", 
                                                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="ratio vs ref.", marker=".",
                                                ax=ax2, legend=False, label=name, color=color)

        # Add grid
        ax1.grid(ls="dashed", c="0.85")
        ax2.grid(ls="dashed", c="0.85")
        # ax2.set_ylim([0, 2])

        # Plot and save
        plot_path = plot_dir + "profile_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=300)
        print("  - generated plot '", plot_path + "'", sep="")

def observation():
    print("5) Running observation plane analysis")

    # Define which columns to plot and corresponding labels, titles and tags
    pdg=[11, 13, 22, 100]
    cols = ["ep", "muon", "photon", "hadron"]
    title = [r"$e^{\pm}$", r"$\mu^{\pm}$", "photons", "hadrons"]
    tag = ["ep", "muon", "photon", "hadron"]

    # Dictionary for dataframes
    res = {}

    # Iterate over runs
    for path in sim_dir:
        # Calculate R from (x,y)
        data[path]["particles"]["R"] = pow(pow(data[path]["particles"]["x"],2) + pow(data[path]["particles"]["y"],2), 0.5)

        res[path] = data[path]["particles"]

    # Plotting of kinetic energy
    for n in range(len(cols)):
        # Create figure
        fig, ax = plt.subplots()

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Get index of this run
            id = sim_dir.index(path)
            # Get color
            color = colors[id]

            # Get 95th percentile for kinetic energy
            T_max = max(0, res[path][abs(res[path]["pdg"]) == pdg[n]]["kinetic_energy"].quantile(0.95))

            # Plot
            res[path][abs(res[path]["pdg"]) == pdg[n]].hist(column="kinetic_energy", ax=ax, bins=128,
            range=[0, T_max], color=color, log=True, histtype="step")

        # Add grid
        ax.grid(ls="dashed", c="0.85")

        # Set title and axis labels
        plt.title("Kinetic energy at observation plane - " + title[n])
        plt.xlabel("$T$ [GeV]")
        plt.ylabel("$N$")
    
        # Set legend
        legend = [name.split("/")[1] for name in sim_dir]
        # if (len(legend) > 1):
            # legend[0] += " (ref)"
        plt.legend(legend)

        # Plot and save
        plot_path = plot_dir + "observ_Ekin_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=300)
        print("  - generated plot '", plot_path + "'", sep="")

    # Plotting of radius
    for n in range(len(cols)):
        # Create figure
        fig, ax = plt.subplots()

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Get index of this run
            id = sim_dir.index(path)
            # Get color
            color = colors[id]

            # Get 99th percentile for radius
            R_max = max(0, res[path][abs(res[path]["pdg"]) == pdg[n]]["R"].quantile(0.99))

            # Plot
            res[path][abs(res[path]["pdg"]) == pdg[n]].hist(column="R", ax=ax, bins=128, range=[0, R_max], color=color, log=True, histtype="step")

        # Add grid
        ax.grid(ls="dashed", c="0.85")

        # Set title and axis labels
        plt.title("Radius at observation plane - " + title[n])
        plt.xlabel("$R$ [m]")
        plt.ylabel("$N$")

        # Set legend
        legend = [name.split("/")[1] for name in sim_dir]
        # if (len(legend) > 1):
        #     legend[0] += " (ref)"
        plt.legend(legend)

        # Plot and save
        plot_path = plot_dir + "observ_R_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=300)
        print("  - generated plot '", plot_path + "'", sep="")

def runtimes():
    print("6) Running runtime analysis")
    
    # Dictionary for dataframes
    res = {}
    
    # Iterate over runs
    for path in sim_dir:
        res[path] = data[path]["runtime"]
        
        res[path]["rt_per_sh"] = res[path]["runtime"] / res[path]["showers"]

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
    # if (len(legend) > 1):
    #     legend[0] += " (ref)"
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
    fig.savefig(plot_path, dpi=300)
    print("  - generated plot '", plot_path + "'", sep="")

# Check if any arguments were passed
if len(sys.argv) == 1:
    print("No simulation name(s) passed")
    print_usage()
    exit(1)

# Limit max X in plots
X_limit = 1100

# Plot directory
plot_dir = "plots/out/"
os.makedirs(plot_dir, exist_ok=True)

# Map modules and output files inside
output_types = {"energyloss": "dEdX",
                "interactions": "interactions",
                "particles": "particles",
                "production_profile": "profile",
                "profile": "profile"}

# Colors in plots
colors=("firebrick", "mediumblue", "green", "goldenrod")

# ---- END OF INPUT ----

# Declare dictionaries to hold dataframes
data = {}

print("Passed ", len(sys.argv)-1, " argument(s), verifying run validity:", sep="")

# Check whether run directories are valid
sim_dir = []
for sim_name in sys.argv[1:]:
    print("  -", sim_name, end=": ")

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

print("Loaded data")

# Analysis
energyloss()
interactions()
production()
profile()
observation()
runtimes()

print("All done")

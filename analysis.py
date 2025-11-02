#!/usr/bin/python3
# Script for analysis of Corsika8 outputs

import pandas as pd
import os
import sys
from matplotlib import pyplot as plt


def print_usage():
    print("Usage")

def energyloss():
    print("1) Running energy loss analysis")

    # Dictionary for dataframes
    res = {}

    # Create figure
    fig, ax = plt.subplots()

    # Iterate over runs
    for path in sim_dir:
        # Parse run name
        name = path.split("/")[1]
        # Get index of this run
        id = sim_dir.index(path)
        # If this run is ref, add that to its name
        if (id == 0): name += " (ref)"
        # Get color
        color = colors[id]

        # Calculate means and SEMs for columns
        res[path] = data[path]["energyloss"].groupby("X").agg({"total":["mean", "sem"]})
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

        # Plot
        res[path][res[path]["X"] < X_limit].plot(x="X", y="total_mean", yerr="total_sem", title="Total energy loss",
                                                grid=True, xlabel="$X$ [g/cm$^2$]", ylabel="$E_{loss}$ [GeV]", marker=".",
                                                ax=ax, legend=plot_legend, label=name, color=color)
    # Add grid
    ax.grid(ls="dashed", c="0.85")

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

    # Iterate over runs and calculate means and SEMs for columns
    for path in sim_dir:
        res[path] = data[path]["production_profile"].groupby("X").agg(["mean", "sem"])
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

    # Iterate over plots
    for n in range(len(cols)):
        # Create figure
        fig, ax = plt.subplots()

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Parse run name
            name = path.split("/")[1]
            # Get index of this run
            id = sim_dir.index(path)
            # If this run is ref, add that to its name
            if (id == 0): name += " (ref)"
            # Get color
            color = colors[id]

            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_mean", yerr=cols[n] + "_sem", title="Avg. number of " + title[n] + " produced per shower",
                                                    grid=True, xlabel="$X$ [g/cm$^2$]", ylabel=label[n] + "^{prod}$", marker=".",
                                                    ax=ax, legend=plot_legend, label=name, color=color)
        # Add grid
        ax.grid(ls="dashed", c="0.85")

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

    # Iterate over runs and calculate means and SEMs for columns
    for path in sim_dir:
        # Add values for positive and negative particles
        data[path]["profile"]["muon"] = data[path]["profile"]["muplus"] + data[path]["profile"]["muminus"]
        data[path]["profile"]["ep"] = data[path]["profile"]["electron"] + data[path]["profile"]["positron"]

        # Calculate means and SEMs for columns
        res[path] = data[path]["profile"].groupby("X").agg(["mean", "sem"])
        res[path].columns = res[path].columns.map('_'.join)
        res[path] = res[path].reset_index()

    # Iterate over plots
    for n in range(len(cols)):
        # Create figure
        fig, ax = plt.subplots()

        # Iterate over runs and generate plots
        for path in sim_dir:
            # Parse run name
            name = path.split("/")[1]
            # Get index of this run
            id = sim_dir.index(path)
            # If this run is ref, add that to its name
            if (id == 0): name += " (ref)"
            # Get color
            color = colors[id]

            # Plot
            res[path][res[path]["X"] < X_limit].plot(x="X", y=cols[n] + "_mean", yerr=cols[n] + "_sem", title="Longitudinal profile - " + title[n],
                                                    grid=True, xlabel="$X$ [g/cm$^2$]", ylabel=label[n], marker=".",
                                                    ax=ax, legend=plot_legend, label=name, color=color)
        # Add grid
        ax.grid(ls="dashed", c="0.85")

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
            res[path][abs(res[path]["pdg"]) == pdg[n]].hist(column="kinetic_energy", ax=ax, bins=128, range=[0, T_max], color=color)

        # Remove grid
        ax.grid(False)

        # Set title and axis labels
        plt.title("Kinetic energy at observation plane - " + title[n])
        plt.xlabel("$T$ [GeV]")
        plt.ylabel("$N$")

        # Set legend
        legend = [name.split("/")[1] for name in sim_dir]
        if (len(legend) > 1):
            legend[0] += " (ref)"
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
            res[path][abs(res[path]["pdg"]) == pdg[n]].hist(column="R", ax=ax, bins=128, range=[0, R_max],color=color)

        # Remove grid
        ax.grid(False)

        # Set title and axis labels
        plt.title("Radius at observation plane - " + title[n])
        plt.xlabel("$R$ [m]")
        plt.ylabel("$N$")

        # Set legend
        legend = [name.split("/")[1] for name in sim_dir]
        if (len(legend) > 1):
            legend[0] += " (ref)"
        plt.legend(legend)

        # Plot and save
        plot_path = plot_dir + "observ_R_" + tag[n] + ".png"
        fig.savefig(plot_path, dpi=300)
        print("  - generated plot '", plot_path + "'", sep="")


# Check if any arguments were passed
if len(sys.argv) == 1:
    print("No simulation name(s) passed")
    print_usage()
    exit(1)

# Limit max X in plots
X_limit = 1200

# Plot directory
plot_dir = "plots/out1/"
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

print("Found", len(sim_dir), "valid runs")

# If plotting multiple runs, enable plot legend
plot_legend = False
if (len(sim_dir) > 1):
    print("Using run \'", sim_dir[0].split("/")[1], "\' as reference", sep="")
    plot_legend=True

# Iterate over output directories and files
for path in sim_dir:
    # print("- processing run '", path, "'", sep="")

    for mod, file in output_types.items():
        # print("   - processing module '", mod, "' (file '", path+mod+"/"+file, ".parquet')", sep="")

        # Compose sim file name
        sim_file = path + mod + "/" + file + ".parquet"

        # Read from parquet file as dataframe
        data[path][mod] = pd.read_parquet(sim_file, "pyarrow")


print("Loaded data")

# Analysis
energyloss()
interactions()
production()
profile()
observation()
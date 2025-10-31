#!/usr/bin/python3
# Script for analysis of Corsika8 outputs

import pandas as pd
import os
import sys
import matplotlib as plt

def energyloss():
    print("Running energy loss analysis")

    # Calculate Edep mean and SEM
    res = data["energyloss"].groupby("X").agg({"total":["mean", "sem"]})
    res.columns = res.columns.map('_'.join)
    res = res.reset_index()

    # Plot
    fig = res[res["X"] < X_limit].plot("X", "total_mean", yerr="total_sem", figsize=(6,4),
          title="Total energy loss", grid=False, xlabel="X [g/cm$^2$]", ylabel="Energy loss [GeV]", legend=False)
    plot_path = plot_dir + "energyloss.png"
    fig.get_figure().savefig(plot_path, dpi=300)
    print("  - generated plot '", plot_path + "'", sep="")

def interactions():
    print("Running interactions analysis")

def production():
    print("Running production analysis")
    
    # print(data["production_profile"]["electron-positron"].sum())

    # Calculate Edep mean and SEM
    res = data["production_profile"].groupby("X").agg(["mean", "sem"])
    res.columns = res.columns.map('_'.join)
    res = res.reset_index()

    # Plot 
    fig = res[res["X"] < X_limit].plot(x="X", y=["electron-positron_mean", "muon_mean", "photon_mean", "hadron_mean"],
        figsize=(6,4), title="Avg. particles produced per shower", grid=False, xlabel="X [g/cm$^2$]", ylabel="Particle production", logy=True)
    fig.legend([r"$e^{\pm}$", r"$\mu^{\pm}$", r"$\gamma$", "hadr."])
   
    plot_path = plot_dir + "prod.png"
    fig.get_figure().savefig(plot_path, dpi=300)
    print("  - generated plot '", plot_path + "'", sep="")

def profile():
    print ("Running longitudinal profile analysis")
    
    # Calculate Edep mean and SEM
    data["profile"]["muon"] = data["profile"]["muplus"] + data["profile"]["muminus"]
    data["profile"]["ep"] = data["profile"]["electron"] + data["profile"]["positron"]

    res = data["profile"].groupby("X").agg(["mean", "sem"])
    res.columns = res.columns.map('_'.join)
    res = res.reset_index()
    # print(res)

    # Plot 
    fig = res[res["X"] < X_limit].plot(x="X", y=["ep_mean", "muon_mean", "photon_mean", "hadron_mean"],
        figsize=(6,4), title="Longitudinal shower profile", grid=False, xlabel="X [g/cm$^2$]", ylabel="Particle population", logy=True)
    fig.legend([r"$e^{\pm}$", r"$\mu^{\pm}$", r"$\gamma$", "hadr."])
   
    plot_path = plot_dir + "profile.png"
    fig.get_figure().savefig(plot_path, dpi=300)
    print("  - generated plot '", plot_path + "'", sep="")

# Limit max X in plots
X_limit = 1500

# Directory with simulation outputs
sim_name = sys.argv[1]
sim_dir = "output/" + sim_name + "/merged/"

# Check if merged directory exists
if not os.path.exists(sim_dir):
    print("Dir does not exist")

plot_dir = "plots/" + sim_name + "/"

os.makedirs(plot_dir, exist_ok=True)

print ("Simulation data dir: '", sim_dir, "'", sep="")

# Map modules and output files inside
output_types = {"energyloss": "dEdX",
                "interactions": "interactions",
                "particles": "particles",
                "production_profile": "profile",
                "profile": "profile"}

# Declare dictionaries to hold dataframes
data = {}

# Iterate over output directories and files
for mod, file in output_types.items():
    print("  - processing module '", mod, "' (file '", file, ".parquet')", sep="")

    # Compose sim file name
    sim_file = sim_dir + mod + "/" + file + ".parquet"

    # Read from parquet file as dataframe
    data[mod] = pd.read_parquet(sim_file, "pyarrow")

# Analysis
energyloss()
interactions()
production()
profile()
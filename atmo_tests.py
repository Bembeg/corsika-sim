#!/usr/bin/python3

import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np


# load test outputs
path = "data/atmo_tests.txt"

# open input file
with open(path, "r") as in_file:
    # get file content
    in_content = in_file.readlines()

# create temp files for processed test results
path_dens = "data/csv_dens.txt"
path_gram = "data/csv_gram.txt"
path_arclen = "data/csv_arclen.txt"

with open(path_dens, "w") as csv_dens:
    csv_dens.write("alt,diff\n")

    with open(path_gram, "w") as csv_gram:
        csv_gram.write("downward,alt0,alt1,len,ang,diff\n")

        with open(path_arclen, "w") as csv_arclen:
            csv_arclen.write("downward,alt0,alt1,len,ang,diff\n")

            for line in in_content:
                line_split = line.strip().split()

                # parse density results
                if "Dens:" in line:
                    # get altitude
                    alt = line_split[5]
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_dens.write(",".join([alt,diff]) + "\n")

                # parse integrated grammage results
                if "Gram:" in line:
                    # track direction
                    downward = "1" if line_split[4] == "do" else "0"
                    # track endpoint altitudes
                    alt0 = line_split[7]
                    alt1 = line_split[10]
                    # track length
                    track_len = line_split[12].strip("(")
                    # track inclination
                    ang = line_split[16].strip("):")
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_gram.write(",".join([downward,alt0,alt1,track_len,ang,diff]) + "\n")

                # parse arclength results
                if "Arclen:" in line:
                    # track direction
                    downward = "1" if line_split[4] == "do" else "0"
                    # track endpoint altitudes
                    alt0 = line_split[7]
                    alt1 = line_split[10]
                    # track length
                    track_len = line_split[12].strip("(")
                    # track inclination
                    ang = line_split[16].strip("):")
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_arclen.write(",".join([downward,alt0,alt1,track_len,ang,diff]) + "\n")

# Load created csv files as dataframes
df_dens = pd.read_csv(path_dens)
df_gram = pd.read_csv(path_gram)
df_arclen = pd.read_csv(path_arclen)

# print(df_dens)
# print(df_gram)
# print(df_arclen)

dpi_val = 300

os.makedirs("plots/atmo_tests", exist_ok=True)

colors = ["red", "orange", "green", "blue", "violet", "black"]

angles = [0, 5, 20, 80, 89, 89.9]

# -----------------
# ---- DENSITY ----
# -----------------
print("Processing density test results")
fig, ax = plt.subplots()
df_dens[df_dens["alt"] < 99000].plot(x="alt", y="diff", title="density", xlabel="altitude [m]", ylabel=r"$\frac{interp. atmo}{expon. atmo} - 1$", legend=None, ax=ax)
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/atmo_tests/density.png", dpi=dpi_val)

# ------------------
# ---- GRAMMAGE ----
# ------------------
print("Processing integrated grammage test results")

# Get abs(diff) for negative values
df_gram["absdiff"] = df_gram["diff"].abs()

for ang in angles:
    fig, ax = plt.subplots()
    # logscale
    ax.set_xscale("log")
    ax.set_yscale("log")
    # grid under points
    ax.set_axisbelow(True)

    # plot tracks with positive diff
    df_gram[(df_gram["ang"] == ang) & (df_gram["diff"] > 0)].plot.scatter(x="len",y="diff",
        title="integrated grammage, track angle " + str(ang) + "°", xlabel="track length [m]",
        ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c="red", alpha=0.3, label="positive diff tracks")
        
    # plot tracks with negative diff
    df_gram[(df_gram["ang"] == ang) & (df_gram["diff"] < 0)].plot.scatter(x="len",y="absdiff",
        title="integrated grammage, track angle " + str(ang) + "°", xlabel="track length [m]",
        ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c="blue", alpha=0.3, label="negative diff tracks")

    # grid
    ax.grid(ls="dashed", c="0.85")
    # save fig
    fig.savefig("plots/atmo_tests/gram_ang" + str(ang) + ".png", dpi=dpi_val)
    # clear fig
    plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["alt0"] < 100000) & (df_gram["diff"] > 0)].plot.scatter(x="len",y="diff", title="integrated grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="track angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/gram_posDiff.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["alt0"] < 100000) & (df_gram["diff"] < 0)].plot.scatter(x="len",y="diff", title="integrated grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="track angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/gram_negDiff.png", dpi=dpi_val)
# clear fig
plt.clf()


# -------------------
# ---- ARCLENGTH ----
# -------------------
print("Processing arclength test results")
for ang in angles:
    fig, ax = plt.subplots()
    # logscale
    ax.set_xscale("log")
    ax.set_yscale("log")
    # grid under points
    ax.set_axisbelow(True)

    # plot downward tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["downward"] == 1)].plot.scatter(x="len",y="diff",
        title="track length from grammage, track angle " + str(ang) + "°", xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c="red", alpha=0.3, label="downward tracks")
    # plot upward tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["downward"] == 0)].plot.scatter(x="len",y="diff",
        title="track length from grammage, track angle " + str(ang) + "°", xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c="blue", alpha=0.3, label="upward tracks")
    # grid
    ax.grid(ls="dashed", c="0.85")
    # save fig
    fig.savefig("plots/atmo_tests/arclen_ang" + str(ang) + ".png", dpi=dpi_val)
    # clear fig
    plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in [89.9, 89, 80, 0]:
    # plot tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["alt0"] < 100000)].plot.scatter(x="len",y="diff",title="track length from grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/arclen.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots()
filt = df_arclen[ (df_arclen["ang"] == 89.9) | (df_arclen["ang"] == 89) | (df_arclen["ang"] == 80) | (df_arclen["ang"] == 0) ]
filt = filt[ (df_arclen["len"] > 1e3) & (df_arclen["diff"] > 1e-5) ]
print(filt)

filt[df_arclen["ang"] == 89.9].plot.scatter(x="len",y="diff", ax=ax, color=colors[0], label="angle 89.9°")
filt[df_arclen["ang"] == 89].plot.scatter(x="len",y="diff", ax=ax, color=colors[1], label="angle 89°")
filt[df_arclen["ang"] == 80].plot.scatter(x="len",y="diff", ax=ax, color=colors[2], label="angle 80°", title="track length outliers", xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$")

# logscale
ax.set_xscale("log")
ax.set_yscale("log")
fig.savefig("plots/atmo_tests/arclen_outliers.png", dpi=dpi_val)

fig, ax = plt.subplots()
ax.set_xscale("log")
filt[df_arclen["ang"] == 89.9].plot.scatter(x="len",y="alt0", ax=ax, color=colors[0], label="angle 89.9°")
filt[df_arclen["ang"] == 89].plot.scatter(x="len",y="alt0", ax=ax, color=colors[1], label="angle 89°")
filt[df_arclen["ang"] == 80].plot.scatter(x="len",y="alt0", ax=ax, color=colors[2], label="angle 80°", title="track length outliers", xlabel="track length [m]", ylabel="track startpoint altitude [m]")
fig.savefig("plots/atmo_tests/arclen_outliers2.png", dpi=dpi_val)
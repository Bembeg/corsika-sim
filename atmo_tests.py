#!/usr/bin/python3

import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


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
    csv_dens.write("alt,densExp,densInt,diff\n")

    with open(path_gram, "w") as csv_gram:
        csv_gram.write("downward,alt0,alt1,len,ang,diff\n")

        with open(path_arclen, "w") as csv_arclen:
            csv_arclen.write("downward,alt0,alt1,len,ang,diff\n")

            for line in in_content:
                line_split = line.strip().split()

                # parse density results
                if "Dens:" in line:
                    # get altitude
                    alt = line_split[5].strip(",")
                    # get density from exponential atmo
                    densExp = line_split[7].strip(",")
                    # get density from interpolated atmo
                    densInt = line_split[9].strip(",")
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_dens.write(",".join([alt,densExp,densInt,diff]) + "\n")

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

angles = [0, 40, 80, 89]

atmo_edges = [0, 7e3, 11.4e3, 37e3, 100e3, 112.8e3]

# -----------------
# ---- DENSITY ----
# -----------------
print("Processing density test results")

edge_around = 5
i = 0
for edge in atmo_edges:
    fig, ax = plt.subplots(constrained_layout=True)
    # fig.set_figwidth(6)
    # get axis range from dataframe
    filt = df_dens[ (df_dens["alt"] > edge-edge_around) & (df_dens["alt"] < edge+edge_around) ]
    mins = filt.min()
    ymin = min(mins["densExp"], mins["densInt"])
    maxs = filt.max()
    ymax = max(maxs["densExp"], maxs["densInt"])

    ax.set_xlim([edge - edge_around, edge + edge_around])
    ax.set_ylim([ymin, ymax])
    # ax.set_yscale("log")
    df_dens.plot(x="alt", y="densExp", ax=ax, label="expon. atm.", color=colors[3], marker=".", markersize=10)
    df_dens.plot(x="alt", y="densInt", title="density at layer boundary - " + str(edge / 1e3) + " km", color=colors[0], xlabel="altitude [m]", ylabel="density [g/cm$^3$]", label="interp. atm.", ax=ax)

    ax.plot([edge, edge], [ymin, ymax], linestyle="dotted", color="black", linewidth=1)

    ax.grid(ls="dashed", c="0.85")
    fig.savefig("plots/atmo_tests/density" + str(i) + ".png", dpi=dpi_val)
    plt.close(fig)
    i += 1


# ------------------
# ---- GRAMMAGE ----
# ------------------
print("Processing integrated grammage test results")

# Get abs(diff) for negative values
df_gram["absdiff"] = df_gram["diff"].abs()

for ang in angles:
    fig, ax = plt.subplots(constrained_layout=True)
    # logscale
    ax.set_xscale("log")
    ax.set_yscale("log")
    # grid under points
    ax.set_axisbelow(True)

    # plot tracks with negative diff
    df_gram[(df_gram["ang"] == ang) & (df_gram["diff"] < 0) & (df_gram["absdiff"] > 1e-11)].plot.scatter(x="len",y="absdiff",
        title="integrated grammage, track angle " + str(ang) + "°", xlabel="track length [m]",
        ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c="red", alpha=0.3, label="negative diff tracks")

    # plot tracks with positive diff
    df_gram[(df_gram["ang"] == ang) & (df_gram["diff"] > 0) & (df_gram["absdiff"] > 1e-11)].plot.scatter(x="len",y="diff",
        title="integrated grammage, track angle " + str(ang) + "°", xlabel="track length [m]",
        ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c="blue", alpha=0.3, label="positive diff tracks")

    # grid
    ax.grid(ls="dashed", c="0.85")
    # save fig
    fig.savefig("plots/atmo_tests/gram_ang" + str(ang) + ".png", dpi=dpi_val)
    # clear fig
    plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["absdiff"] > 1e-11) & (df_gram["diff"] > 0)].plot.scatter(x="len",y="diff", title="integrated grammage - positive diff tracks",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="track angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/gram_posDiff.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["absdiff"] > 1e-11) & (df_gram["diff"] < 0)].plot.scatter(x="len",y="absdiff", title="integrated grammage - negative diff tracks",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="track angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/gram_negDiff.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["absdiff"] > 1e-11)].plot.scatter(x="len",y="absdiff", title="integrated grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="track angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/gram.png", dpi=dpi_val)
# clear fig
plt.clf()


# -------------------
# ---- ARCLENGTH ----
# -------------------
print("Processing arclength test results")

# Get abs(diff) for negative values
df_arclen["absdiff"] = df_arclen["diff"].abs()

for ang in angles:
    fig, ax = plt.subplots(constrained_layout=True)
    # logscale
    ax.set_xscale("log")
    ax.set_yscale("log")
    # grid under points
    ax.set_axisbelow(True)

    # plot tracks with negative diff
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["diff"] < 0)].plot.scatter(x="len",y="absdiff",
        title="track length from grammage, track angle " + str(ang) + "°", xlabel="track length [m]",
        ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c="red", alpha=0.3, label="negative diff tracks")

    # plot upward tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["diff"] > 0)].plot.scatter(x="len",y="diff",
        title="track length from grammage, track angle " + str(ang) + "°", xlabel="track length [m]",
        ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c="blue", alpha=0.3, label="positive diff tracks")

    # grid
    ax.grid(ls="dashed", c="0.85")
    # save fig
    fig.savefig("plots/atmo_tests/arclen_ang" + str(ang) + ".png", dpi=dpi_val)
    # clear fig
    plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["diff"] < 0)].plot.scatter(x="len",y="absdiff",title="track length from grammage - negative diff tracks",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/arclen_negDiff.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["diff"] > 0)].plot.scatter(x="len",y="diff",title="track length from grammage - positive diff tracks",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/arclen_posDiff.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots(constrained_layout=True)
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
for ang in angles:
    # plot tracks
    df_arclen[(df_arclen["ang"] == ang)].plot.scatter(x="len",y="absdiff",title="track length from grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atm.}{expon. atm.} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")
# save fig
fig.savefig("plots/atmo_tests/arclen.png", dpi=dpi_val)
# clear fig
plt.clf()


# -------------------
# ---- OUTLIERS- ----
# -------------------

# filter data for outliers
ang_filt = df_arclen[ (df_arclen["ang"] == 89) | (df_arclen["ang"] == 80) | (df_arclen["ang"] == 40) ]
xmin = 1e3
xmax = 1e6
filt = ang_filt[ (ang_filt["len"] > xmin) & (ang_filt["absdiff"] > 1e-5) ]
print("Filtered arclength dataframe:", filt.count()["len"], "tracks")

# make new plot
fig, ax = plt.subplots(constrained_layout=True)
fig.set_figwidth(7)

# plot outliers
filt[filt["ang"] == 40].plot.scatter(x="len",y="alt0", ax=ax, color=colors[1], label="angle 40°")
filt[filt["ang"] == 80].plot.scatter(x="len",y="alt0", ax=ax, color=colors[2], label="angle 80°")
filt[filt["ang"] == 89].plot.scatter(x="len",y="alt0", ax=ax, color=colors[3], label="angle 89°", xlabel="track length [m]", ylabel="track startpoint altitude [m]", title="track length from grammage - outliers")

# logscale and axis limits
ax.set_xscale("log")
# ax.set_yscale("log")
ax.set_xlim([xmin, xmax])

# plot atmosphere layer boundaries
for edge in atmo_edges:
    ax.plot([xmin, xmax], [edge, edge], linestyle="dotted", color="black", linewidth=1)

fig.savefig("plots/atmo_tests/arclen_outliers.png", dpi=dpi_val)

# filter data for outliers
ang_filt = df_gram[ (df_gram["ang"] == 89) | (df_gram["ang"] == 80) | (df_gram["ang"] == 40) ]
xmin = 1e3
xmax = 1e6
filt = ang_filt[ (ang_filt["len"] > xmin) & (ang_filt["absdiff"] > 1e-5) ]
print("Filtered grammage dataframe:", filt.count()["len"], "tracks")

fig, ax = plt.subplots(constrained_layout=True)

filt[filt["ang"] == 40].plot.scatter(x="len",y="alt0", ax=ax, color=colors[1], label="angle 40°")
filt[filt["ang"] == 80].plot.scatter(x="len",y="alt0", ax=ax, color=colors[2], label="angle 80°")
filt[filt["ang"] == 89].plot.scatter(x="len",y="alt0", ax=ax, color=colors[3], label="angle 89°", xlabel="track length [m]", ylabel="track startpoint altitude [m]", title="integrated grammage - outliers")

# logscale
ax.set_xscale("log")
ax.set_xlim([xmin, xmax])
fig.set_figwidth(7)
# ax.set_yscale("log")

for edge in atmo_edges:
    ax.plot([xmin, xmax], [edge, edge], linestyle="dotted", color="black", linewidth=1)

fig.savefig("plots/atmo_tests/gram_outliers.png", dpi=dpi_val)

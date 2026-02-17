#!/usr/bin/python3

import pandas as pd
import os
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
                    diff = str(abs(float(line_split[-1])))
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

os.makedirs("plots/atmo_tests", exist_ok=True)

# -----------------
# ---- DENSITY ----
# -----------------
print("Processing density test results")
fig, ax = plt.subplots()
df_dens[df_dens["alt"] < 99000].plot(x="alt", y="diff", title="density", xlabel="altitude [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", legend=None, ax=ax)
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/atmo_tests/density.png", dpi=300)

print("  accumulated diffs:", df_dens.sum()["diff"])

# ------------------
# ---- GRAMMAGE ----
# ------------------
print("Processing integrated grammage test results")
for ang in [0, 10, 45, 85]:
    fig, ax = plt.subplots()
    # logscale
    ax.set_xscale("log")
    ax.set_yscale("log")
    # grid under points
    ax.set_axisbelow(True)

    # plot downward tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["downward"] == 1)].plot.scatter(x="len",y="diff",
        title="integrated grammage, track angle " + str(ang) + "°", xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c="red", alpha=0.3, label="downward tracks")
    # plot upward tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["downward"] == 0)].plot.scatter(x="len",y="diff",
        title="integrated grammage, track angle " + str(ang) + "°", xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c="blue", alpha=0.3, label="upward tracks")
    # grid
    ax.grid(ls="dashed", c="0.85")    
    # save fig
    fig.savefig("plots/atmo_tests/gram_ang" + str(ang) + ".png", dpi=300)
    # clear fig
    plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
colors = ["red", "orange", "green", "blue", ]
for ang in [0, 10, 45, 85]:
    # plot tracks
    df_gram[(df_gram["ang"] == ang) & (df_gram["alt0"] < 100000)].plot.scatter(x="len",y="diff", title="integrated grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="track angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")    
# save fig
fig.savefig("plots/atmo_tests/gram.png", dpi=300)
# clear fig
plt.clf()


# -------------------
# ---- ARCLENGTH ----
# -------------------
print("Processing arclength test results")
for ang in [0, 45, 85]:
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
    fig.savefig("plots/atmo_tests/arclen_ang" + str(ang) + ".png", dpi=300)
    # clear fig
    plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

i=0
colors = ["red", "green", "blue"]
for ang in [0, 45, 85]:
    # plot tracks
    df_arclen[(df_arclen["ang"] == ang) & (df_arclen["alt0"] < 100000)].plot.scatter(x="len",y="diff",title="track length from grammage",
     xlabel="track length [m]", ylabel=r"abs$\left[\frac{interp. atmo}{expon. atmo} - 1\right]$", ax=ax, c=colors[i], alpha=1, label="angle " + str(ang) + "°")
    i += 1

# grid
ax.grid(ls="dashed", c="0.85")    
# save fig
fig.savefig("plots/atmo_tests/arclen.png", dpi=300)
# clear fig
plt.clf()

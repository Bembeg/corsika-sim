#!/usr/bin/python3

import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


# load test outputs
path = "data/tracktests-inlayer.txt"
name = "layer"

# Load csv files as dataframes
df = pd.read_csv(path)

os.makedirs("plots/track_tests", exist_ok=True)

colors = ["red", "orange", "green", "blue", "violet", "black"]

dpi_val = 450

# add ratio columns
df["d_gramIntSingle"] = df["gramIntSingle"] / df["gramExp"] - 1
df["d_gramInt"] = df["gramInt"] / df["gramExp"] - 1
df["d_gramExp"] = df["gramExp"] / df["gramExp"] - 1
df["d_lenIntSingle"] = df["lenIntSingle"] / df["lenExp"] - 1
df["d_lenInt"] = df["lenInt"] / df["lenExp"] - 1
df["d_lenExp"] = df["lenExp"] / df["lenExp"] - 1
df["da_gramIntSingle"] = abs( df["gramIntSingle"] / df["gramExp"] - 1 )
df["da_gramInt"] = abs( df["gramInt"] / df["gramExp"] - 1 )
df["da_gramExp"] = abs( df["gramExp"] / df["gramExp"] - 1 )
df["da_lenIntSingle"] = abs( df["lenIntSingle"] / df["lenExp"] - 1 )
df["da_lenInt"] = abs( df["lenInt"] / df["lenExp"] - 1 )
df["da_lenExp"] = abs( df["lenExp"] / df["lenExp"] - 1 )

# GRAMMAGE - length
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
plt.subplots_adjust(hspace=0.05)
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)
ax1.set_yscale("log")
ax2.set_yscale("log")
ax1.set_axisbelow(True)
ax2.set_axisbelow(True)
# main plot
df.plot(x="length", y="gramExp", label="expon. atm.", ax=ax1, color=colors[0], marker=".")
df.plot(x="length", y="gramIntSingle", label="interp. atm.", ax=ax1, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track length [m]",
    ylabel = "integr. gram. [g/cm$^2$]")
# ratio plot
df.plot(x="length", y="da_gramIntSingle", label=None, legend=None, ax=ax2, color=colors[2], marker=".", title=None, xlabel="track length [m]",
    ylabel = r"$abs\left[\frac{interp. atm.}{expon. atm.} - 1\right]$")
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/gram_" + name + "_trLen.png", dpi=dpi_val)

# GRAMMAGE - angle
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
plt.subplots_adjust(hspace=0.05)
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)
ax1.set_yscale("log")
ax2.set_yscale("log")
ax1.set_axisbelow(True)
ax2.set_axisbelow(True)
# main plot
df.plot(x="angle", y="gramExp", label="expon. atm.", ax=ax1, color=colors[0], marker=".")
df.plot(x="angle", y="gramIntSingle", label="interp. atm.", ax=ax1, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track zenith angle [deg]",
    ylabel = "integr. gram. [g/cm$^2$]")
# ratio plot
df.plot(x="angle", y="da_gramIntSingle", label=None, legend=None, ax=ax2, color=colors[2], marker=".", title=None, xlabel="track zenith angle [deg]",
    ylabel = r"$abs\left[\frac{interp. atm.}{expon. atm.} - 1\right]$")
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/gram_" + name + "_trAng.png", dpi=dpi_val)

# TRACK LENGTH - length
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
plt.subplots_adjust(hspace=0.05)
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)
ax1.set_axisbelow(True)
ax2.set_axisbelow(True)
# ax1.set_yscale("log")
ax2.set_yscale("log")
# main plot
df.plot(x="length", y="lenExp", label="expon. atm.", ax=ax1, color=colors[0], marker=".")
df.plot(x="length", y="lenIntSingle", label="interp. atm.", ax=ax1, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track length [m]",
    ylabel = "length from gram. [m]")
# ratio plot
df.plot(x="length", y="da_lenIntSingle", label=None, legend=None, ax=ax2, color=colors[2], marker=".", title=None, xlabel="track length [m]",
    ylabel = r"$abs\left[\frac{interp. atm.}{expon. atm.} - 1\right]$")
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/len_" + name + "_trLen.png", dpi=dpi_val)

# TRACK LENGTH - angle
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
plt.subplots_adjust(hspace=0.05)
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)
ax1.set_axisbelow(True)
ax2.set_axisbelow(True)
# ax1.set_yscale("log")
ax2.set_yscale("log")
# main plot
df.plot(x="angle", y="lenExp", label="expon. atm.", ax=ax1, color=colors[0], marker=".")
df.plot(x="angle", y="lenIntSingle", label="interp. atm.", ax=ax1, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track zenith angle [deg]",
    ylabel = "length from gram. [m]")
# ratio plot
df.plot(x="angle", y="da_lenIntSingle", label=None, legend=None, ax=ax2, color=colors[2], marker=".", title=None, xlabel="track zenith angle [deg]",
    ylabel = r"$abs\left[\frac{interp. atm.}{expon. atm.} - 1\right]$")
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/len_" + name + "_trAng.png", dpi=dpi_val)

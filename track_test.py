#!/usr/bin/python3

import os
import sys
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


# load test outputs
path = "data/tracktests-inlayer.txt"

# Load csv files as dataframes
df = pd.read_csv(path)

os.makedirs("plots/track_tests", exist_ok=True)

colors = ["red", "orange", "green", "blue", "violet", "black"]

dpi_val = 300

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

# GRAMMAGE
fig, ax = plt.subplots()
df.plot(x="length", y="d_gramExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="length", y="d_gramIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track length [m]",
    ylabel = r"$\frac{integr.~gram.~(~*~atm.)}{integr.~gram.~(expon. atm.)} - 1$")
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/gram_layer_trLen_lin.png", dpi=dpi_val)

fig, ax = plt.subplots()
df.plot(x="length", y="da_gramExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="length", y="da_gramIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track length [m]",
    ylabel = r"$abs\left[\frac{integr.~gram.~(~*~atm.)}{integr.~gram.~(expon. atm.)} - 1\right]$")
ax.grid(ls="dashed", c="0.85")
ax.set_yscale("log")
fig.savefig("plots/track_tests/gram_layer_trLen_log.png", dpi=dpi_val)

fig, ax = plt.subplots()
df.plot(x="angle", y="d_gramExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="angle", y="d_gramIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track zenith angle [deg]",
    ylabel = r"$\frac{integr.~gram.~(~*~atm.)}{integr.~gram.~(expon. atm.)} - 1$")
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/gram_layer_trAng_lin.png", dpi=dpi_val)

fig, ax = plt.subplots()
df.plot(x="angle", y="da_gramExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="angle", y="da_gramIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track zenith angle [deg]",
    ylabel = r"$abs\left[\frac{integr.~gram.~(~*~atm.)}{integr.~gram.~(expon. atm.)} - 1\right]$")
ax.grid(ls="dashed", c="0.85")
ax.set_yscale("log")
fig.savefig("plots/track_tests/gram_layer_trAng_log.png", dpi=dpi_val)


# TRACK LENGTHS
fig, ax = plt.subplots()
df.plot(x="length", y="d_lenExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="length", y="d_lenIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track length [m]",
    ylabel = r"$\frac{track~length~(~*~atm.)}{track~length~(expon. atm.)} - 1$")
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/len_layer_trLen_lin.png", dpi=dpi_val)

fig, ax = plt.subplots()
df.plot(x="length", y="da_lenExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="length", y="da_lenIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track length [m]",
    ylabel = r"$abs\left[\frac{track~length~(~*~atm.)}{track~length~(expon. atm.)} - 1\right]$")
ax.grid(ls="dashed", c="0.85")
ax.set_yscale("log")
fig.savefig("plots/track_tests/len_layer_trLen_log.png", dpi=dpi_val)

fig, ax = plt.subplots()
df.plot(x="angle", y="d_lenExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="angle", y="d_lenIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track zenith angle [deg]",
    ylabel = r"$\frac{track~length~(~*~atm.)}{track~length~(expon. atm.)} - 1$")
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/track_tests/len_layer_trAng_lin.png", dpi=dpi_val)

fig, ax = plt.subplots()
df.plot(x="angle", y="da_lenExp", label="expon. atm.", ax=ax, color=colors[0], marker=".")
df.plot(x="angle", y="da_lenIntSingle", label="interp. atm.", ax=ax, color=colors[2], marker=".", title="test tracks between R0 = 99 km and R1 = 38 km", xlabel="track zenith angle [deg]",
    ylabel = r"$abs\left[\frac{track~length~(~*~atm.)}{track~length~(expon. atm.)} - 1\right]$")
ax.grid(ls="dashed", c="0.85")
ax.set_yscale("log")
fig.savefig("plots/track_tests/len_layer_trAng_log.png", dpi=dpi_val)

#!/usr/bin/python3

import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np
import math

# load test outputs
path_exp = "data/trackdump_1e3_expon.txt"
path_int = "data/trackdump_1e3_interp.txt"

# make output directory
os.makedirs("plots/trackdump", exist_ok=True)

# linestyles and colors
linestyles = ["solid", "dotted"]
colors = ["red", "orange", "green", "blue"]

# steering
dpi_val = 450
n_bins = 32
colW = 9

# inputs
columns = ["len", "ang", "gram", "alt0", "alt1"]
logX = [True, False, True, True, True]
label = ["track lengths", "track angles", "traversed integrated grammage", "track startpoint altitudes", "track endpoint altitudes"]
axis_label = ["track length [m]", "track angle [deg]", "traversed integrated grammage [g/cm2]", "track startpoint altitude [m]", "track endpoint altitude [m]"]

# load created csv files as dataframes
df_exp = pd.read_csv(path_exp)
df_int = pd.read_csv(path_int)

# process individual columns
for i in range(len(columns)):
    print("Processing '", columns[i], "'", sep="")

    # make new plot
    fig = plt.figure()
    ax = plt.subplot(111)

    fig.set_figwidth(10)

    # x-axis logscale
    if (logX[i]):
        ax.set_xscale("log")

    # grid below points
    ax.set_axisbelow(True)

    # add grid
    ax.grid(ls="dashed", c="0.85")

    # define binning
    bin_min = df_exp[df_exp[columns[i]]>0].min()[columns[i]]
    bin_max = df_exp.max()[columns[i]]
    if (logX[i]):
        bins = np.logspace(np.log10(bin_min), np.log10(bin_max), n_bins)
    else:
        bins = np.linspace(bin_min, bin_max, n_bins)

    # add histograms to plot
    df_exp[df_exp["step"] == "geom"].hist(column=columns[i], ax=ax, bins=bins, color=colors[0], histtype="step", log=True, linestyle=linestyles[0])
    df_int[df_int["step"] == "geom"].hist(column=columns[i], ax=ax, bins=bins, color=colors[0], histtype="step", log=True, linestyle=linestyles[1])
    df_exp[df_exp["step"] == "inter"].hist(column=columns[i], ax=ax, bins=bins, color=colors[1], histtype="step",log=True, linestyle=linestyles[0])
    df_int[df_int["step"] == "inter"].hist(column=columns[i], ax=ax, bins=bins, color=colors[1], histtype="step",log=True, linestyle=linestyles[1])
    df_exp[df_exp["step"] == "decay"].hist(column=columns[i], ax=ax, bins=bins, color=colors[2], histtype="step",log=True, linestyle=linestyles[0])
    df_int[df_int["step"] == "decay"].hist(column=columns[i], ax=ax, bins=bins, color=colors[2], histtype="step",log=True, linestyle=linestyles[1])
    df_exp[df_exp["step"] == "cont"].hist(column=columns[i], ax=ax, bins=bins, color=colors[3], histtype="step",log=True, linestyle=linestyles[0])
    df_int[df_int["step"] == "cont"].hist(column=columns[i], ax=ax, bins=bins, color=colors[3], histtype="step",log=True, linestyle=linestyles[1])

    # set title and axis labels
    plt.title("distribution of " + label[i] + " per track type")
    plt.xlabel(axis_label[i])
    plt.ylabel("$N$")

    # shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.75, box.height])

    # legend
    legend =  ["geom. limit - expon."]
    legend += ["geom. limit - interp."]
    legend += ["interaction - expon."]
    legend += ["interaction - interp."]
    legend += ["decay - expon."]
    legend += ["decay - interp."]
    legend += ["cont. limit - expon."]
    legend += ["cont. limit - interp."]
    plt.legend(legend, fontsize="small", loc="upper left", frameon=False, bbox_to_anchor=(1.01, 1.015))

    # y-axis range
    # ax.set_ylim(1, 1e10)

    # Counters
    n_geom_exp = df_exp[df_exp["step"] == "geom"].count()["len"]
    n_geom_int = df_int[df_int["step"] == "geom"].count()["len"]
    n_inter_exp = df_exp[df_exp["step"] == "inter"].count()["len"]
    n_inter_int = df_int[df_int["step"] == "inter"].count()["len"]
    n_decay_exp = df_exp[df_exp["step"] == "decay"].count()["len"]
    n_decay_int = df_int[df_int["step"] == "decay"].count()["len"]
    n_cont_exp = df_exp[df_exp["step"] == "cont"].count()["len"]
    n_cont_int = df_int[df_int["step"] == "cont"].count()["len"]

    # text description
    text =  "(Cumulative across 10 showers)\n\n"
    text += " TRACK TYPE | EXPON.  | INTERP. \n"
    text += "--------------------------------\n"
    text += "geom. limit |" \
        + " " + str(n_geom_exp) \
        + " " * (colW - len(str(n_geom_exp)) - 1) \
        + "|" + " " + str(n_geom_int) \
        + " " * (colW - len(str(n_geom_int)) - 1) + "\n"
    text += "interaction |" \
        + " " + str(n_inter_exp) \
        + " " * (colW - len(str(n_inter_exp)) - 1) \
        + "|" + " " + str(n_inter_int) \
        + " " * (colW - len(str(n_inter_int)) - 1) + "\n"
    text += "      decay |" \
        + " " + str(n_decay_exp) \
        + " " * (colW - len(str(n_decay_exp)) - 1) \
        + "|" + " " + str(n_decay_int) \
        + " " * (colW - len(str(n_decay_int)) - 1) + "\n"
    text += "cont. limit |" \
        + " " + str(n_cont_exp) \
        + " " * (colW - len(str(n_cont_exp)) - 1) \
        + "|" + " " + str(n_cont_int) \
        + " " * (colW - len(str(n_cont_int)) - 1) + "\n"

    plt.text(1.02, 0.3, text, family="Monospace", horizontalalignment='left',
     verticalalignment='top', fontsize="x-small", transform = ax.transAxes)

    # save fig
    fig.savefig("plots/trackdump/1e3/" + columns[i] + ".png", dpi = dpi_val)

    # clear fig
    plt.clf()

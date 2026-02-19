#!/usr/bin/python3

import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np

# load test outputs
path_exp = "data/trackdump_expon.txt"
path_int = "data/trackdump_interp.txt"

os.makedirs("plots/trackdump", exist_ok=True)

dpi_val = 300

# load created csv files as dataframes
df_exp = pd.read_csv(path_exp)
df_int = pd.read_csv(path_int)

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
# grid under points
ax.set_axisbelow(True)

# define binning
ang_min = df_exp[df_exp["len"]>0].min()["len"]
ang_max = df_exp.max()["len"]
bins = np.logspace(np.log10(ang_min), np.log10(ang_max), 64)

# Add grid
ax.grid(ls="dashed", c="0.85")

df_exp[df_exp["step"] == "geom"].hist(column="len", ax=ax, bins=bins, color="red", histtype="step", log=True)
df_exp[df_exp["step"] == "inter"].hist(column="len", ax=ax, bins=bins, color="orange", histtype="step",log=True)
df_exp[df_exp["step"] == "decay"].hist(column="len", ax=ax, bins=bins, color="green", histtype="step",log=True)
df_exp[df_exp["step"] == "cont"].hist(column="len", ax=ax, bins=bins, color="blue", histtype="step",log=True)
df_exp.hist(column="len", ax=ax, bins=bins, color="blue", alpha=0, histtype="step",log=True)

# set title and axis labels
plt.title("Step length distribution per step type - exponential atmo.")
plt.xlabel("Step length [m]")
plt.ylabel("$N$")

n_geom = df_exp[df_exp["step"] == "geom"].count()["len"]
n_inter = df_exp[df_exp["step"] == "inter"].count()["len"]
n_decay = df_exp[df_exp["step"] == "decay"].count()["len"]
n_cont = df_exp[df_exp["step"] == "cont"].count()["len"]
n_tot = df_exp.count()["len"]

# legend
legend = ["geom. limit (" + str(n_geom) + ", " + str("{:.2f}".format(n_geom/n_tot*100)) + "%)"]
legend += ["interaction (" + str(n_inter) + ", " + str("{:.2f}".format(n_inter/n_tot*100)) + "%)"]
legend += ["decay (" + str(n_decay) + ", " + str("{:.2f}".format(n_decay/n_tot*100)) + "%)"]
legend += ["cont. limit (" + str(n_cont) + ", " + str("{:.2f}".format(n_cont/n_tot*100)) + "%)"]
legend += ["total (" + str(n_tot) + ")"]
plt.legend(legend)

ax.set_ylim(1, 8e6)

# grid
ax.grid(ls="dashed", c="0.85")    
# save fig
fig.savefig("plots/trackdump/len_expon.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_xscale("log")
# grid under points
ax.set_axisbelow(True)

# define binning
ang_min = df_int[df_int["len"]>0].min()["len"]
ang_max = df_int.max()["len"]
bins = np.logspace(np.log10(ang_min), np.log10(ang_max), 64)

# Add grid
ax.grid(ls="dashed", c="0.85")

df_int[df_int["step"] == "geom"].hist(column="len", ax=ax, bins=bins, color="red", histtype="step", log=True)
df_int[df_int["step"] == "inter"].hist(column="len", ax=ax, bins=bins, color="orange", histtype="step",log=True)
df_int[df_int["step"] == "decay"].hist(column="len", ax=ax, bins=bins, color="green", histtype="step",log=True)
df_int[df_int["step"] == "cont"].hist(column="len", ax=ax, bins=bins, color="blue", histtype="step",log=True)
df_int.hist(column="len", ax=ax, bins=bins, color="blue", alpha=0, histtype="step",log=True)

# set title and axis labels
plt.title("Step length distribution per step type - interpolated atmo.")
plt.xlabel("Step length [m]")
plt.ylabel("$N$")

n_geom = df_int[df_int["step"] == "geom"].count()["len"]
n_inter = df_int[df_int["step"] == "inter"].count()["len"]
n_decay = df_int[df_int["step"] == "decay"].count()["len"]
n_cont = df_int[df_int["step"] == "cont"].count()["len"]
n_tot = df_int.count()["len"]

# legend
legend = ["geom. limit (" + str(n_geom) + ", " + str("{:.2f}".format(n_geom/n_tot*100)) + "%)"]
legend += ["interaction (" + str(n_inter) + ", " + str("{:.2f}".format(n_inter/n_tot*100)) + "%)"]
legend += ["decay (" + str(n_decay) + ", " + str("{:.2f}".format(n_decay/n_tot*100)) + "%)"]
legend += ["cont. limit (" + str(n_cont) + ", " + str("{:.2f}".format(n_cont/n_tot*100)) + "%)"]
legend += ["total (" + str(n_tot) + ")"]
plt.legend(legend)

ax.set_ylim(1, 8e6)

# grid
ax.grid(ls="dashed", c="0.85")    
# save fig
fig.savefig("plots/trackdump/len_interp.png", dpi=dpi_val)
# clear fig
plt.clf()


fig, ax = plt.subplots()
# logscale
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

# Add grid
ax.grid(ls="dashed", c="0.85")

df_exp[df_exp["step"] == "geom"].hist(column="ang", ax=ax, bins=180, color="red", histtype="step")
df_exp[df_exp["step"] == "inter"].hist(column="ang", ax=ax, bins=180, color="orange", histtype="step")
df_exp[df_exp["step"] == "decay"].hist(column="ang", ax=ax, bins=180, color="green", histtype="step")
df_exp[df_exp["step"] == "cont"].hist(column="ang", ax=ax, bins=180, color="blue", histtype="step")
df_exp.hist(column="ang", ax=ax, bins=180, color="blue", alpha=0, histtype="step")

# set title and axis labels
plt.title("Track angle distribution per step type - exponential atmo.")
plt.xlabel("Track angle [deg]")
plt.ylabel("$N$")

n_geom = df_exp[df_exp["step"] == "geom"].count()["len"]
n_inter = df_exp[df_exp["step"] == "inter"].count()["len"]
n_decay = df_exp[df_exp["step"] == "decay"].count()["len"]
n_cont = df_exp[df_exp["step"] == "cont"].count()["len"]
n_tot = df_exp.count()["len"]

# legend
legend = ["geom. limit (" + str(n_geom) + ", " + str("{:.2f}".format(n_geom/n_tot*100)) + "%)"]
legend += ["interaction (" + str(n_inter) + ", " + str("{:.2f}".format(n_inter/n_tot*100)) + "%)"]
legend += ["decay (" + str(n_decay) + ", " + str("{:.2f}".format(n_decay/n_tot*100)) + "%)"]
legend += ["cont. limit (" + str(n_cont) + ", " + str("{:.2f}".format(n_cont/n_tot*100)) + "%)"]
legend += ["total (" + str(n_tot) + ")"]
plt.legend(legend)

ax.set_ylim(1, 5e5)

# grid
ax.grid(ls="dashed", c="0.85")    
# save fig
fig.savefig("plots/trackdump/ang_expon.png", dpi=dpi_val)
# clear fig
plt.clf()

fig, ax = plt.subplots()
# logscale
ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)
# bins = np.linspace(0, 180, 360)

# Add grid
ax.grid(ls="dashed", c="0.85")

df_int[df_int["step"] == "geom"].hist(column="ang", ax=ax, bins=180, color="red", histtype="step")
df_int[df_int["step"] == "inter"].hist(column="ang", ax=ax, bins=180, color="orange", histtype="step")
df_int[df_int["step"] == "decay"].hist(column="ang", ax=ax, bins=180, color="green", histtype="step")
df_int[df_int["step"] == "cont"].hist(column="ang", ax=ax, bins=180, color="blue", histtype="step")
df_int.hist(column="ang", ax=ax, bins=180, color="blue", alpha=0, histtype="step")

# set title and axis labels
plt.title("Track angle distribution per step type - interpolated atmo.")
plt.xlabel("Track angle [deg]")
plt.ylabel("$N$")

n_geom = df_int[df_int["step"] == "geom"].count()["len"]
n_inter = df_int[df_int["step"] == "inter"].count()["len"]
n_decay = df_int[df_int["step"] == "decay"].count()["len"]
n_cont = df_int[df_int["step"] == "cont"].count()["len"]
n_tot = df_int.count()["len"]

# legend
legend = ["geom. limit (" + str(n_geom) + ", " + str("{:.2f}".format(n_geom/n_tot*100)) + "%)"]
legend += ["interaction (" + str(n_inter) + ", " + str("{:.2f}".format(n_inter/n_tot*100)) + "%)"]
legend += ["decay (" + str(n_decay) + ", " + str("{:.2f}".format(n_decay/n_tot*100)) + "%)"]
legend += ["cont. limit (" + str(n_cont) + ", " + str("{:.2f}".format(n_cont/n_tot*100)) + "%)"]
legend += ["total (" + str(n_tot) + ")"]
plt.legend(legend)

ax.set_ylim(1, 5e5)

# grid
ax.grid(ls="dashed", c="0.85")    
# save fig
fig.savefig("plots/trackdump/ang_interp.png", dpi=dpi_val)
# clear fig
plt.clf()
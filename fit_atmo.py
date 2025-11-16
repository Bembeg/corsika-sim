#!/usr/bin/python3

import pandas as pd
import os
import sys
from matplotlib import pyplot as plt
from math import exp
from scipy.optimize import curve_fit
import numpy as np

def fit_expo(x, offset, scale):
    return offset/scale * np.exp(-x*100000/scale)*1000


def calculate_density(H, model):
    offset = model[-1][1]
    scale = model[-1][2]
    for set in model:
        if (H < set[0]):
            offset = set[1]
            scale = set[2]
            break

    return offset/scale * exp(-(H)*100000/scale)*1000


model_USStd = [[7, 1183.6071, 954248.34],
               [11.4, 1143.0425, 800005.34],
               [37, 1322.9748, 629568.93],
               [100, 655.67307, 737521.77]]

model_Linsley = [[4, 1222.6562, 994186.38],
                 [10, 1144.9069, 878153.55],
                 [40, 1305.5948, 636143.04],
                 [100, 540.1778, 772170.16]]

# Load atmosphere csv
par = pd.read_csv("AtmoUSStd.csv")

model_fit = []

# Fit density
step = 5
bounds = [-1, 3, 7, 11, 16, 22, 28, 35, 40, 45, 50, 61, 86, 150]
for i in range(len(bounds)):
    if (i == len(bounds)-1):
        # model_fit.append([112.8, 1, 1e9])
        break

    print("Fitting density profile in range", bounds[i], "-", bounds[i+1])
    param_alt = par["altitude"][(bounds[i] <= par["altitude"]) & (par["altitude"] <= bounds[i+1])]
    param_dens = par["density"][(bounds[i] <= par["altitude"]) & (par["altitude"] <= bounds[i+1])]
    param_bounds = [[200,300000],[1700, 1.5e6]]
    param_prior = [700, 7e5]

    if (i == len(bounds)-2):
        param_bounds =[[100,300000],[1700, 1.5e6]]
        param_prior = [700, 7e5]


    popt, pcov = curve_fit(fit_expo, param_alt, param_dens, p0=param_prior, bounds=param_bounds)
    print(" - offset:", popt[0], "scale:", popt[1])
    model_fit.append([bounds[i+1], popt[0], popt[1]])


# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
# Set vertical gap between subplots
plt.subplots_adjust(hspace=0.05)

# Calculate density from C7 models
par["dens_USStd"] = [calculate_density(H, model_USStd) for H in par["altitude"]]
par["dens_Linsley"] = [calculate_density(H, model_Linsley) for H in par["altitude"]]
par["dens_fit"] = [calculate_density(H, model_fit) for H in par["altitude"]]
# Calculate ratio to reference
par["ratio_USStd"] = par["dens_USStd"] / par["density"]
par["ratio_Linsley"] = par["dens_Linsley"] / par["density"]
par["ratio_fit"] = par["dens_fit"] / par["density"]

# Print fit chi2
print("fit chi2:", sum([pow(abs(x-1),2) for x in par["ratio_fit"][par["altitude"]<110]]))

# Plot density plot
par.plot(x="altitude", y=["dens_USStd", "dens_Linsley", "dens_fit", "density"], ax=ax1,
    label=["C7 US-std", "C7 Linsley", "fit", "Tab US-std"], xlabel="Altitude [km]", ylabel="Density [kg/m$^3$]")
# Ratio plot
par.plot(x="altitude", y=["ratio_USStd", "ratio_Linsley", "ratio_fit"], ax=ax2, label=["C7: US-std", "C7: Linsley", "Fit"],
 xlabel="Altitude [km]", ylabel="C7 / tab", legend=False)

ax1.set_xlim([-1, 12])
ax2.set_ylim([0.9, 1.1])
# Set x-axis ticks for subplots
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)

# Add grid
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
# Logscale
# ax1.set_yscale("log")

ax1.set_xlim(-1, 110)
ax1.set_ylim(1e-5, 1.5)
ax2.set_ylim(0.5, 2.4)
# Save
fig.savefig("plots/atmo_fit/density.png", dpi=300)

# Plot boundaries for models
for set in model_USStd:
    plt.axvline(set[0], ls="dashed", lw=0.6, c="tab:blue")
for set in model_Linsley:
    plt.axvline(set[0], ls="dashed", lw=0.6, c="tab:orange")
for set in model_fit:
    plt.axvline(set[0], ls="dashed", lw=0.6, c="tab:green")
plt.axhline(1, lw=1, c="black", ls="dashed")


x_limits = [[-1,12], [12,30], [30,45], [45,70], [70,110]]
y_main_limits = [[0.3, 1.4], [0.01, 0.33], [0.0001, 0.02], [2e-5, 0.0022], [1e-8, 9e-5]]
y_ratio_limits = [[0.985, 1.03], [0.97, 1.01], [0.95, 1.05], [0.8, 1.07], [0., 2.4]]
# Draw options

os.makedirs("plots/atmo_fit", exist_ok=True)

for i in range(len(x_limits)):
    ax1.set_xlim(x_limits[i][0], x_limits[i][1])
    ax1.set_ylim(y_main_limits[i][0], y_main_limits[i][1])
    ax2.set_ylim(y_ratio_limits[i][0], y_ratio_limits[i][1])
    # Save
    fig.savefig("plots/atmo_fit/density_" + str(i+1) + ".png", dpi=300)



# calculate(model_USStd)

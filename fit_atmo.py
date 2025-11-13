#!/usr/bin/python3

import pandas as pd
import os
import sys
from matplotlib import pyplot as plt
from math import exp

def calculate_density(H, model):
    alt = model[-1][0]
    offset = model[-1][1]
    scale = model[-1][2]
    for set in model:
        if (H < set[0]):
            alt = set[0]
            offset = set[1]
            scale = set[2]
            break 
        
    # print("alt:", H, "height:", alt, "offset", offset, "scale", scale)
    # dens = offset/scale * exp(-(H)*100000/scale)*1000
    # print("alt:", H, "dens:", dens)

    return offset/scale * exp(-(H)*100000/scale)*1000
    

model_USStd = [[7, 1183.6071, 954248.34],
               [11.4, 1143.0425, 800005.34],
               [37, 1322.9748, 629568.93],
               [100, 655.67307, 737521.77],
               [112.8, 1, 1e9]]

model_Linsley = [[4, 1222.6562, 994186.38],
                 [10, 1144.9069, 878153.55],
                 [40, 1305.5948, 636143.04],
                 [100, 540.1778, 772170.16],
                 [112.8, 1, 1e9]]

# Load atmosphere csv
par = pd.read_csv("AtmoUSStd.csv")

# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
# Set vertical gap between subplots
plt.subplots_adjust(hspace=0.05)

# Calculate density from C7 models
par["dens_USStd"] = [calculate_density(H, model_USStd) for H in par["altitude"]]
par["dens_Linsley"] = [calculate_density(H, model_Linsley) for H in par["altitude"]]
# Calculate ratio to reference
par["ratio_USStd"] = par["dens_USStd"] / par["density"]
par["ratio_Linsley"] = par["dens_Linsley"] / par["density"]

# Plot density plot
par.plot(x="altitude", y=["dens_USStd", "dens_Linsley", "density"], ax=ax1,
    label=["C7 US-std", "C7 Linsley", "Tab US-std"], xlabel="Altitude [km]", ylabel="Density [kg/m$^3$]")
# Ratio plot
par.plot(x="altitude", y=["ratio_USStd", "ratio_Linsley"], ax=ax2, label=["C7: US-std", "C7: Linsley"],
 xlabel="Altitude [km]", ylabel="C7 / tab")

ax1.set_xlim([-1, 80])
ax2.set_ylim([0.7, 1.3])
# Set x-axis ticks for subplots
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)

# Draw options
# Add grid
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
ax1.set_yscale("log")

# Save
fig.savefig("test.png", dpi=300)

# calculate(model_USStd)



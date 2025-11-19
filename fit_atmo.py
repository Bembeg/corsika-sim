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

# Two models from C7/C8
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

# Empty array for fit model
model_fit = []

# Fit boundaries
bounds = [-1, 3, 7, 11, 16, 22, 28, 35, 40, 45, 50, 61, 86, 110]

print("Fitting density profile:")
print("  Range\t\tOffset\t\tScale")
print("  -------------------------------------")
for i in range(len(bounds)-1):
    print("  ",bounds[i], "-", bounds[i+1],end="\t\t", sep="")
    
    # Filter altitude and density for this range
    param_alt = par["altitude"][(bounds[i] <= par["altitude"]) & (par["altitude"] <= bounds[i+1])]
    param_dens = par["density"][(bounds[i] <= par["altitude"]) & (par["altitude"] <= bounds[i+1])]
    
    # Set limits for fit parameters
    param_bounds = [[200,300000],[1700, 1.5e6]]
    # Set priors for fit parameters
    param_prior = [700, 7e5]
    # Set limits and priors specifically for the last layer
    if (i == len(bounds)-2):
        param_bounds =[[100,300000],[1700, 1.5e6]]
        param_prior = [700, 7e5]

    # Fit tabulated density
    popt, pcov = curve_fit(fit_expo, param_alt, param_dens, p0=param_prior, bounds=param_bounds)
    print(round(popt[0],1), "\t\t", round(popt[1],1),sep="")
    
    # Add fit parameters to model list
    model_fit.append([bounds[i+1], popt[0], popt[1]])

# Create figure
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.5, 0.5])
# Set vertical gap between subplots
plt.subplots_adjust(hspace=0.05)

# Calculate density from C7 and fit models
par["dens_USStd"] = [calculate_density(H, model_USStd) for H in par["altitude"]]
par["dens_Linsley"] = [calculate_density(H, model_Linsley) for H in par["altitude"]]
par["dens_fit"] = [calculate_density(H, model_fit) for H in par["altitude"]]
# Calculate ratio to reference
par["ratio_USStd"] = par["dens_USStd"] / par["density"]
par["ratio_Linsley"] = par["dens_Linsley"] / par["density"]
par["ratio_fit"] = par["dens_fit"] / par["density"]

# Calculate fit chi2 in several altitude ranges
print("Printing chi2 for models:")
for H in range(0,100,20):
    print(H, "-", H+20, "km", sep="")

    # Number of points in this altitude range
    n_points = len(par["altitude"][(par["altitude"] >= H) & (par["altitude"] < H+20)])
    
    # Fit chi2 for models
    chi2_USStd = sum([pow(abs(x-1),2) for x in par["ratio_USStd"][(par["altitude"] >= H) & (par["altitude"] < H+20)]]) / n_points
    chi2_Linsley = sum([pow(abs(x-1),2) for x in par["ratio_Linsley"][(par["altitude"] >= H) & (par["altitude"] < H+20)]]) / n_points
    chi2_fit = sum([pow(abs(x-1),2) for x in par["ratio_fit"][(par["altitude"] >= H) & (par["altitude"] < H+20)]]) / n_points 
    
    # Print fit chi2
    print("   USStd: {:.8f}".format(chi2_USStd), " (", round(chi2_USStd/chi2_fit, 2), "x)", sep="")
    print(" Linsley: {:.8f}".format(chi2_Linsley), " (", round(chi2_Linsley/chi2_fit, 2), "x)", sep="")
    print("     Fit: {:.8f}".format(chi2_fit), " (-)", sep="")

# Plot density plot
par.plot(x="altitude", y=["dens_USStd", "dens_Linsley", "dens_fit", "density"], ax=ax1,
    label=["C8 US-std-BK", "C8 Linsley", "fit", "tab. US-std"], xlabel="Altitude [km]", ylabel="Density [kg/m$^3$]")
# Ratio plot
par.plot(x="altitude", y=["ratio_USStd", "ratio_Linsley", "ratio_fit"], ax=ax2,
    xlabel="Altitude [km]", ylabel="model / tab.", legend=False)

# Set x-axis ticks for subplots
ax1.tick_params(axis='x', direction='in')
ax2.tick_params(axis='x', direction='in', top=True)

# Add grid
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")

# Logscale
ax1.set_yscale("log")

# Axis ranges
ax1.set_xlim(-1, 110)
ax1.set_ylim(5e-8, 1.5)
ax2.set_ylim(0.5, 2.4)

# Draw vertical line at 1
plt.axhline(1, lw=1, c="black", ls="dashed")

# Make directory for plots
os.makedirs("plots/atmo_fit", exist_ok=True)

# Save plot
fig.savefig("plots/atmo_fit/density.png", dpi=300)

# Plot boundaries for models
for set in model_USStd:
    plt.axvline(set[0], ls="dashed", lw=0.6, c="tab:blue")
for set in model_Linsley:
    plt.axvline(set[0], ls="dashed", lw=0.6, c="tab:orange")
for set in model_fit:
    plt.axvline(set[0], ls="dashed", lw=0.6, c="tab:green")

# Axis ranges for altitude ranges
x_limits = [[-1,20], [20,60], [60,110]]
y_main_limits = [[0.08, 1.4], [0.0002, 0.095], [8e-8, 0.00035]]
y_ratio_limits = [[0.982, 1.035], [0.82, 1.07], [0.5, 5]]

# Plot density for altitude ranges
for i in range(len(x_limits)):
    # Set axis ranges
    ax1.set_xlim(x_limits[i][0], x_limits[i][1])
    ax1.set_ylim(y_main_limits[i][0], y_main_limits[i][1])
    ax2.set_ylim(y_ratio_limits[i][0], y_ratio_limits[i][1])
    # Save plot
    fig.savefig("plots/atmo_fit/density_" + str(i+1) + ".png", dpi=300)

# Dump fit model in C8-usable format
if(True):
    print("Dumping fit model:")
    # Iterate over fit layers
    for n in range(len(model_fit)):
        # Format based on index of layer
        if (n==0): print("{{", end="")
        elif (n==len(model_fit)): print("}},")
        else: print("  ", end="")

        # Print layer parameters
        print("{", model_fit[n][0], "_km, grammage(", "{:.4f}".format(model_fit[n][1]), "), ", "{:.2f}".format(model_fit[n][2]), "_cm},", sep="")
    
    # Add final constant layer
    print("  {112.8_km, grammage(1), 1e9_cm}}},")

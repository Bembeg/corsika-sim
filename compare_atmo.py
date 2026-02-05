#!/usr/bin/python3

import pandas as pd
import os
import sys
from matplotlib import pyplot as plt
from math import exp
from scipy.optimize import curve_fit
import numpy as np

df = pd.read_csv("data/tab_models.csv")
df = df.rename(columns={'#alt[km]': 'alt', 'rho1[g/cm^3]': 'rho1', 'rho2[g/cm^3]': 'rho2', 'rho3[g/cm^3]': 'rho3'})
df["ratio2"] = df["rho2"] / df["rho1"] - 1
df["ratio3"] = df["rho3"] / df["rho1"] - 1

os.makedirs("plots/atmo", exist_ok=True)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.3, 0.7])
plt.subplots_adjust(top=0.925, 
                    bottom=0.20, 
                    left=0.2, 
                    right=0.90, 
                    hspace=0.1, 
                    wspace=0.01)

alt_limit = 120

df[df["alt"] < alt_limit].plot(x="alt", y=["rho1", "rho2"], ax=ax1,
    label=["ref (5layer dump)", "tab (log. int. dump)"], xlabel="Altitude [km]", ylabel="density [g/cm$^3$]")
df[df["alt"] < alt_limit].plot(x="alt", y=["ratio2"], ax=ax2,
    xlabel="Altitude [km]", ylabel="tab/ref - 1", legend=False)
ax1.set_yscale("log")
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")
fig.savefig("plots/atmo/density_log.png", dpi=300)

ax2.set_ylim(-0.00011, 0.00011)
fig.savefig("plots/atmo/density_log_excl.png", dpi=300)

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, height_ratios=[0.3, 0.7])
plt.subplots_adjust(top=0.925, 
                    bottom=0.20, 
                    left=0.2, 
                    right=0.90, 
                    hspace=0.1, 
                    wspace=0.01)



df[df["alt"] < alt_limit].plot(x="alt", y=["rho1", "rho3"], ax=ax1,
    label=["ref (5layer dump)", "tab (lin. int. dump)"], xlabel="Altitude [km]", ylabel="density [g/cm$^3$]")
df[df["alt"] < alt_limit].plot(x="alt", y=["ratio3"], ax=ax2,
    xlabel="Altitude [km]", ylabel="tab/ref - 1", legend=False)

ax1.set_yscale("log")
ax1.grid(ls="dashed", c="0.85")
ax2.grid(ls="dashed", c="0.85")

fig.savefig("plots/atmo/density_lin.png", dpi=300)

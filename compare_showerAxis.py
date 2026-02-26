#!/usr/bin/python3

import pandas as pd
import os
from matplotlib import pyplot as plt
import numpy as np

# load test outputs
path_ref = "data/showerAxis_ref.txt"
path_impl = "data/showerAxis_impl.txt"

os.makedirs("plots/showerAxis", exist_ok=True)

dpi_val = 300

# load created csv files as dataframes
df_ref = pd.read_csv(path_ref)
df_impl = pd.read_csv(path_impl)

print(df_ref)
print(df_impl)

fig, ax = plt.subplots()

# logscale
# ax.set_xscale("log")
# ax.set_yscale("log")
# grid under points
ax.set_axisbelow(True)

df_impl["ratio"] = df_ref["val"] / df_impl["val"] - 1

# define binning

# Add grid
ax.grid(ls="dashed", c="0.85")

df_impl.plot(x="idx", y="ratio", ax=ax)

# set title and axis labels
plt.title("ShowerAxis comparison")
plt.xlabel("ShowerAxis bin index")
plt.ylabel("Grammage [g/cm^2]")

# save fig
fig.savefig("plots/showerAxis/comparison.png", dpi=dpi_val)

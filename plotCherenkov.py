#!/usr/bin/python3

import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.lines as mlines
from matplotlib import pyplot as plt
from PIL import Image

path = "data/light.parquet"

# Read from parquet file as dataframe
data = pd.read_parquet(path, "pyarrow")

print(data)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
print("Plotting")

ax.scatter(data["hitX"], data["hitY"], data["hitZ"], s=0.8)



ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(0, 3)
# ax.set_axis_off()
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])

print("Making plots for a gif")
ax.elev = 10
idx = 0
plots = []
for azim in range(0, 360, 5):
    ax.azim = azim
    plot_name = "plots/cherenkov/fig_" + "{:02d}".format(idx) + ".png"
    fig.savefig(plot_name, dpi=300)
    plots.append(plot_name)
    idx += 1

print("Making gif")
images = []
for image in plots:
    im = Image.open(image)
    images.append(im)

# save as a gif   
images[0].save('plots/cherenkov/rot.gif',
               save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)

# delete individual gif components
for path in plots:
    os.remove(path)

print("Plotting views")

ax.elev = 90
ax.azim = -90
fig.savefig("plots/cherenkov/view_z.png", dpi=300)

ax.elev = 0
ax.azim = 0
fig.savefig("plots/cherenkov/view_x.png", dpi=300)

ax.elev = 0
ax.azim = -90
fig.savefig("plots/cherenkov/view_y.png", dpi=300)


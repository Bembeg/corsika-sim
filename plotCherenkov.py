#!/usr/bin/python3

import os
import sys
import numpy as np
import pandas as pd
from scipy.stats import norm
import matplotlib.lines as mlines
from matplotlib import pyplot as plt
from PIL import Image
import yaml

def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)

    if (c==1):
        return np.identity(3)

    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

pathData = "data/light.parquet"
pathConf = "data/config.yaml"

# read data 
data = pd.read_parquet(pathData, "pyarrow")

# read config
with open(pathConf, "r") as fileConf:
    conf = yaml.safe_load(fileConf)

print(conf)
print(data)

# plot observer collection



fig = plt.figure()
ax = fig.add_subplot(projection='3d')

print("Plotting")


colors=("black", "firebrick", "mediumblue", "green", "goldenrod", "skyblue", "lightpink")

# ax.scatter(data["hitX"], data["hitY"], data["hitZ"], s=0.8, c=data["time"], cmap="viridis")

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
# observer info
idx = 0
for name in conf["observers"]:
    center = conf["observers"][name]["position"]
    pointing = conf["observers"][name]["pointing"]
    radius = conf["observers"][name]["radius"]
    print(f"Observer {name}: pos {center}, pointing {pointing}, radius {radius}")

    # plot center points and pointing direction
    scale = 0.3
    ax.plot([center[0], center[0]+pointing[0]*scale], [center[1], center[1]+pointing[1]*scale], [center[2], center[2]+pointing[2]*scale],color=colors[idx],marker=".")

    # plot observer outline - draw circle in XY plane
    phi = np.linspace(0, 2*np.pi, 201)
    outl = [radius * np.cos(phi), radius * np.sin(phi), 0*phi]

    # Calculate rotation matrix to align circle with the pointing direction
    rotation_matrix = rotation_matrix_from_vectors([0,0,1], pointing)

    # Apply rotation
    outl_rot = np.dot(rotation_matrix, np.array(outl))

    ax.plot(outl_rot[0] + center[0], outl_rot[1] + center[1], outl_rot[2] + center[2], color=colors[idx])

    idx += 1

fig.savefig("plots/cherenkov/obsColl.png", dpi=300)

ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
ax.set_zlim(0, 3)
ax.set_axis_off()
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])

# print("Making plots for a gif")
# ax.elev = 10
# idx = 0
# plots = []
# for azim in range(0, 360, 5):
#     ax.azim = azim
#     plot_name = "plots/cherenkov/fig_" + "{:02d}".format(idx) + ".png"
#     fig.savefig(plot_name, dpi=300)
#     plots.append(plot_name)
#     idx += 1

# print("Making gif")
# images = []
# for image in plots:
#     im = Image.open(image)
#     images.append(im)

# # save as a gif   
# images[0].save('plots/cherenkov/rot.gif',
#                save_all=True, append_images=images[1:], optimize=False, duration=100, loop=0)

# # delete individual gif components
# for path in plots:
#     os.remove(path)

print("Plotting views")
ax.elev = 45
ax.azim = 60
fig.savefig("plots/cherenkov/obsColl_view.png", dpi=300)

ax.elev = 90
ax.azim = -90
fig.savefig("plots/cherenkov/obsColl_z.png", dpi=300)

ax.elev = 5
ax.azim = 180
fig.savefig("plots/cherenkov/obsColl_x.png", dpi=300)

ax.elev = 5
ax.azim = -90
fig.savefig("plots/cherenkov/obsColl_y.png", dpi=300)


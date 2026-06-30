#!/usr/bin/python3

import os
import sys
import math
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

# global configs
colors=("black", "firebrick", "mediumblue", "green", "goldenrod", "skyblue", "lightpink")
n_bins = 32
n_bins_fine = 128
dpi_val = 300
dashed_linestyle = (0, (1,1))

# input paths
path = sys.argv[1] + "/"
sim = sys.argv[2] + "/"

plot_path = "plots/cherenkov/" + sim

print(f"Processing simulation data: {sim}")

# make dir for plots
os.makedirs(plot_path, exist_ok=True)

# read data 
data = pd.read_parquet(path + sim + "cherenkov/light.parquet", "pyarrow")

# read config
with open(path + sim + "cherenkov/config.yaml", "r") as fileConf:
    conf = yaml.safe_load(fileConf)

# print("\nPrinting input")
# print(conf)
# print(data)

n_hits = data.count()["hitX"]
print(f"Hits in data: {n_hits}")

# -------------------------
# -- OBSERVER COLLECTION --
# -------------------------
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
# remove axis labels
# ax.set_axis_off()
ax.set_xticklabels([])
ax.set_yticklabels([])
ax.set_zticklabels([])

print("Observer collection in data:")

observer_idx = 0
for name in conf["observers"]:
    center = conf["observers"][name]["position"]
    pointing = conf["observers"][name]["pointing"]
    radius = conf["observers"][name]["radius"]
    print(f" - {name}: pos {center}, pointing {pointing}, radius {radius}")
    
    pointing_scale = radius
    observer_color = colors[observer_idx]

    # plot observer outline - draw circle in XY plane
    phi = np.linspace(0, 2*np.pi, 201)
    outl = [radius * np.cos(phi), radius * np.sin(phi), 0*phi]

    # calculate rotation matrix to align circle with the pointing direction
    rotation_matrix = rotation_matrix_from_vectors([0,0,1], pointing)

    earth_rad = 6371000

    # rotate the circle
    outl_rot = np.dot(rotation_matrix, np.array(outl))

    # draw observer outline projection to ground
    # ax.plot(outl_rot[0] + center[0], outl_rot[1] + center[1], earth_rad, color=observer_color, linestyle=dashed_linestyle)
    # ax.plot([center[0], center[0]+pointing[0]*pointing_scale], [center[1], center[1]+pointing[1]*pointing_scale], [earth_rad, earth_rad], color=observer_color, linestyle=dashed_linestyle, marker="o", markersize=3, markerfacecolor="none")

    # draw observer outline
    ax.plot(outl_rot[0] + center[0], outl_rot[1] + center[1], outl_rot[2] + center[2], color=observer_color)
    ax.plot([center[0], center[0]+pointing[0]*pointing_scale], [center[1], center[1]+pointing[1]*pointing_scale], [center[2], center[2]+pointing[2]*pointing_scale], color=observer_color, marker="o", markersize=3)

    observer_idx += 1

# enforce axis range
lim = 13
ax.set_xlim(-lim, lim)
ax.set_ylim(-lim, lim)
ax.set_zlim(earth_rad, earth_rad+30)
fig.savefig(plot_path + "obs_coll.png", dpi=dpi_val*2)

n_observers = observer_idx

# -----------------
# -- GLOBAL HITS --
# -----------------
if (n_observers > 1):
    print("Multiple observers, making global plots")
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    # remove axis labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_zticklabels([])

    # plot hit positions
    ax.scatter(data["hitX"], data["hitY"], data["hitZ"], s=0.8, c=data["time"], cmap="viridis")
    # enforce axis range
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(earth_rad, earth_rad+30)
    # double DPI value
    fig.savefig(plot_path + "global_hits3D.png", dpi=dpi_val*2)
    plt.close()

    # global histogram of hit timestamps
    fig, ax = plt.subplots()
    counts, bins = np.histogram(data["time"], weights = data["weight"], bins = n_bins)
    ax.stairs(counts, bins)
    ax.set_title("Global photon arrival time")
    ax.set_xlabel("t [ns]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + "global_time.png", dpi=dpi_val)
    plt.close()

    # global histogram of photon wavelengths
    fig, ax = plt.subplots()
    counts, bins = np.histogram(data["wavelength"], weights = data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title("Global photon wavelength")
    ax.set_xlabel("wavelength [nm]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + "global_wavelength.png", dpi=dpi_val)
    plt.close()

    # global histogram of hit positions in all coordinates
    # X position
    fig, ax = plt.subplots()
    counts, bins = np.histogram(data["hitX"], weights = data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title("Global photon X position")
    ax.set_xlabel("hit X [m]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + "global_hitX.png", dpi=dpi_val)
    plt.close()
    # Y position
    fig, ax = plt.subplots()
    counts, bins = np.histogram(data["hitY"], weights = data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title("Global photon Y position")
    ax.set_xlabel("hit Y [m]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + "global_hitY.png", dpi=dpi_val)
    plt.close()
    # Z position
    fig, ax = plt.subplots()
    counts, bins = np.histogram(data["hitZ"], weights = data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title("Global photon Z position")
    ax.set_xlabel("hit Z [m]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + "global_hitZ.png", dpi=dpi_val)
    plt.close()

# -------------------
# -- OBSERVER HITS --
# -------------------
observer_idx = 0
for observer_name in conf["observers"]:
    print(f"Plotting hits in observer {observer_name}")
    center = conf["observers"][observer_name]["position"]
    pointing = conf["observers"][observer_name]["pointing"]
    radius = conf["observers"][observer_name]["radius"]
    
    # filter dataframe for this observer only
    filtered_data = data[data["obsId"] == observer_idx]

    # get timestamp range to define binning
    time_max = filtered_data.max()["time"]
    time_min = filtered_data.min()["time"]
    # time binning in ns
    time_bin = 2
    time_bins = math.ceil((time_max - time_min) / time_bin)

    # time
    fig, ax = plt.subplots()
    counts, bins = np.histogram(filtered_data["time"], weights = filtered_data["weight"], bins = time_bins)
    ax.stairs(counts, bins)
    ax.set_title(f"Photon arrival time in observer {observer_name}")
    ax.set_xlabel("t [ns]")
    ax.set_ylabel("photons")
    # window in ns to plot from the first hit
    time_window = 150
    # ax.set_xlim(time_min, time_min + time_window)
    fig.savefig(plot_path + f"{observer_name}_time.png", dpi=dpi_val)
    plt.close()
    
    # get wavelength range to define binning
    wl_max = filtered_data.max()["wavelength"]
    wl_min = filtered_data.min()["wavelength"]
    # wavelength binning in nm
    wl_bin = 1
    wl_bins = math.ceil((wl_max - wl_min) / wl_bin)

    # wavelength
    fig, ax = plt.subplots()
    counts, bins = np.histogram(filtered_data["wavelength"], weights = filtered_data["weight"], bins = wl_bins)
    ax.stairs(counts, bins)
    ax.set_title(f"Photon wavelength in observer {observer_name}")
    ax.set_xlabel("wavelength [nm]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + f"{observer_name}_wavelength.png", dpi=dpi_val)
    plt.close()

    # X position
    fig, ax = plt.subplots()
    counts, bins = np.histogram(filtered_data["hitX"], weights = filtered_data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title(f"Photon X-position in observer {observer_name}")
    ax.set_xlabel("hit X [m]")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + f"{observer_name}_hitX.png", dpi=dpi_val)
    plt.close()
    # Y position
    fig, ax = plt.subplots()
    counts, bins = np.histogram(filtered_data["hitY"], weights = filtered_data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title(f"Photon Y-position in observer {observer_name}")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + f"{observer_name}_hitY.png", dpi=dpi_val)
    plt.close()
    # Z position
    fig, ax = plt.subplots()
    counts, bins = np.histogram(filtered_data["hitZ"], weights = filtered_data["weight"], bins = n_bins)
    plt.stairs(counts, bins)
    ax.set_title(f"Photon Z-position in observer {observer_name}")
    ax.set_ylabel("photons")
    fig.savefig(plot_path + f"{observer_name}_hitZ.png", dpi=dpi_val)
    plt.close()

    # draw hits in local coordinate frame of the observer
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal")

    # calculate rotation matrix to transform points onto the ground plane
    rotation_matrix = rotation_matrix_from_vectors(pointing, [0, 0, 1])
    # hits in the global coordinate system
    hits = [filtered_data["hitX"] - center[0], filtered_data["hitY"] - center[1], filtered_data["hitZ"] - center[2]]
    # transform hits to observer local coordinate system
    trf_hits = np.dot(rotation_matrix, hits)

    ax.plot(trf_hits[0], trf_hits[1], marker="o", linestyle="none")

    # draw observer outline
    theta = np.linspace(0 , 2*np.pi, 200)
    outl = [radius * np.cos(theta), radius * np.sin(theta)]
    ax.plot(outl[0], outl[1], color="black")

    ax.set_xlim(-radius*1.1, radius*1.1)
    ax.set_ylim(-radius*1.1, radius*1.1)
    ax.set_title(f"Hits in observer {observer_name} (local coordinates)")
    ax.set_xlabel("$X_{loc}$ [m]")
    ax.set_ylabel("$Y_{loc}$ [m]")
    fig.savefig(plot_path + f"{observer_name}_hitProj.png", dpi=dpi_val)
    plt.close()

    # hit position 2D histogram
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_aspect("equal")
    ax.plot(outl[0], outl[1], color="black")
    _,_,_,img = ax.hist2d(trf_hits[0], trf_hits[1], weights = filtered_data["weight"], cmap = "gist_heat_r", bins = n_bins_fine) 
    ax.set_xlim(-radius*1.1, radius*1.1)
    ax.set_ylim(-radius*1.1, radius*1.1)
    ax.set_title(f"Hits in observer {observer_name} (local coordinates)")
    fig.colorbar(img, ax=ax, label="Photon density", pad=0.02, shrink=0.835)    
    ax.set_xlabel("$X_{loc}$ [m]")
    ax.set_ylabel("$Y_{loc}$ [m]")
    fig.savefig(plot_path + f"{observer_name}_hit2D.png", dpi=dpi_val)

    # hit position 2D histogram around observer center
    center_factor = 0.3
    ax.set_xlim(-radius * center_factor, radius * center_factor)
    ax.set_ylim(-radius * center_factor, radius * center_factor)
    fig.savefig(plot_path + f"{observer_name}_hit2D_center.png", dpi=dpi_val)
    plt.close()

    # hit radius
    hit_rad = np.sqrt(np.square(trf_hits[0]) + np.square(trf_hits[1]))
    counts, bins = np.histogram(hit_rad, weights = filtered_data["weight"], bins = n_bins_fine)

    print(counts)
    print(bins)

    for i in range(len(counts)):
        inner_rad = bins[i]
        outer_rad = bins[i+1]
        # print(f"inner_rad {inner_rad}, outer_rad {outer_rad}")
        outer_surf = 2 * 3.1415926 * outer_rad * outer_rad
        inner_surf = 2 * 3.1415926 * inner_rad * inner_rad
        surf = outer_surf - inner_surf
        # scale the histogram bin by the surface area
        counts[i] = counts[i] / surf


    fig, ax = plt.subplots()
    ax.stairs(counts, bins)
    ax.set_title(f"Photon hit radius in observer {observer_name}")
    ax.set_xlabel("radius [m]")
    ax.set_ylabel("photons / m$^2$")
    fig.savefig(plot_path + f"{observer_name}_hitR.png", dpi=dpi_val)

    observer_idx += 1

print()

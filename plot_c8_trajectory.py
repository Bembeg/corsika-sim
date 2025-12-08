import matplotlib.pyplot as plt
import numpy as np
import os
from math import sqrt

# Open and load logfile
file = "log2"
with open("data/" + file + ".txt", "r") as log:
    content = log.readlines()

# Atmosphere layer boundaries
atmo = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
        28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 115, 120]

# Number of points
x = []
y = []
z = []
rad = []
nod = []
ins = []
x_proj = []

# Parse log file
for line in content:
    # New point information starts with its position
    if "Tracking pos" in line:
        print("New point [", len(x), "]:", sep="")

        # Parse point position
        pos = line[line.index("(")+1:line.index(")")]
        print("  pos    :", pos)

        # Add x,y,z positions to arrays
        x.append(float(pos.split()[0]))
        y.append(float(pos.split()[1]))
        z.append(float(pos.split()[2]))

        # Calculate radius and add to array
        radius = sqrt(x[-1]**2 + y[-1]**2 + z[-1]**2)
        rad.append(radius)
        print("  radius :", radius)
        print("  alt    :", radius-6371000)

    if "volumeNode=" in line:
        # Parse node identifier and add to array
        node = line[line.index("=")+1:line.index(",")]
        nod.append(node)
        print("  node   :", node)

        # Parse whether numerically inside the node
        inside = line.rstrip()[line.rindex("=")+1:]
        # Convert string to bool
        inside_bool = True if inside == "true" else False
        # and add to array
        ins.append(inside_bool)
        print("  inside :", inside)

# Projection of position along the axis determined by the two furthest points
fig, ax = plt.subplots()

# Max distance between any two points
max_dist = 0
# Indices of the two points
p1 = 0
p2 = 0

# Find two points furthest apart
for n in range(len(x)):
    for m in range(len(x)):
        # Vector between the points
        v = np.array([x[m]-x[n], y[m]-y[n], z[m]-z[n]])

        # Its norm
        v_norm = np.sqrt(sum(v**2))

        # Update max distance
        if (v_norm > max_dist):
            max_dist = v_norm
            p1 = n
            p2 = m

print("Furthest two points:", p1, "and",  p2)

# Axis is the vector between the two furthest apart points
axis = np.array([x[p2]-x[p1], y[p2]-y[p1], z[p2]-z[p1]])
# Norm of the axis vector
ax_norm = np.sqrt(sum(axis**2))

# Plot individual points
for n in range(len(x)):
    # Vector to the point
    v = np.array([x[n]-x[p1], y[n]-y[p1], z[n]-z[p1]])

    # Its norm
    v_norm = np.sqrt(sum(v**2))

    x_proj.append(v_norm/ax_norm)

    # Plot the point
    plt.plot(x_proj[n], rad[n], marker="o", color="red")
    # Plot line to previous point
    if (n > 0):
        plt.arrow(x_proj[n-1], rad[n-1], x_proj[n]-x_proj[n-1], rad[n]-rad[n-1], color="red", width=0.01)
    # Annotate the current node
    plt.text(x_proj[n]+0.02, rad[n]+100, nod[n][-6:], fontsize="x-small")

# Set axis liimts
ax.set_xlim([-0.1, 1.1])
ax.set_ylim(min(rad)-5000, max(rad)+5000)
ax.set_ylim(min(rad)-1000, max(rad)+1000)

# Vector to earth center and its norm
ec = np.array([-x[0], -y[0], -z[0]])
ec_norm = np.sqrt(sum(ec**2))

# Draw layer boundaries as circles around earth center
for r in atmo:
    circ = plt.Circle((ec_norm/ax_norm, 0), r*1000 +
                      6371000, fill=False, color='blue')
    ax.add_patch(circ)

axis_labels = ax.get_yticks().tolist()
axis_labels_upd = [x-6371000 for x in axis_labels]

ax.set_yticklabels(axis_labels_upd)

# Save plot
fig.savefig("plots/tracking_dbg/" + file + ".png", dpi=300)

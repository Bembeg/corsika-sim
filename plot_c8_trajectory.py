import matplotlib.pyplot as plt
import numpy as np
import os
from math import sqrt

# Open and load logfile
file = "log3"
with open("data/" + file + ".txt", "r") as log:
    content = log.readlines()

# Atmosphere layer boundaries
atmo = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
        28, 29, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 110, 115, 120]

atmo = [7, 11.4, 37, 100, 112.8]

# Number of points
x = []
y = []
z = []
rad = []
nod = []
ins = []
x_proj = []

inside_expected = True
# Parse log file
for line in content:
    # New point information starts with its position
    if "Tracking pos" in line:
        ins.append(inside_expected)
        inside_expected = True
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

    if "expect to be" in line:
        inside_expected = False

ins.append(inside_expected)

fig, ax = plt.subplots()
# ax = fig.add_subplot(projection='3d')
# ax.plot(xs=x,ys=y,zs=z, marker="o", markersize=8, color="blue")
# ax.set_xlabel('X')
# ax.set_ylabel('Y')
# ax.set_zlabel('Z')

# x_min, x_max = ax.get_xlim()
# y_min, y_max = ax.get_ylim()
# z_min, z_max = ax.get_zlim()

# ax.plot(xs=x,ys=y,zs=z_min, color="silver", marker="o",markersize=5)
# ax.plot(xs=[x_min for _ in x],ys=y,zs=z, color="silver", marker="o",markersize=5)
# ax.plot(xs=x,ys=[y_max for _ in y],zs=z, color="silver", marker="o",markersize=5)
# ax.set_xlim(x_min, x_max)
# ax.set_ylim(y_min, y_max)
# ax.set_zlim(z_min, z_max)
# ax.plot(xs=x,ys=y,zs=z, marker="o", markersize=8, color="blue")
# plt.show()

# exit(0)

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

# Vector to earth center and its norm
ec = np.array([-x[0], -y[0], -z[0]])
ec_norm = np.sqrt(sum(ec**2))

# Normal vector to plane formed by axis vector and vector to center
plane_normal = np.cross(axis, ec)
plane_norm = np.sqrt(sum(plane_normal**2))

# Draw layer boundaries as circles around earth center
for r in atmo:
    ax.plot([-0.1, 1.1], [r*1000 + 6371000, r*1000 +6371000], color="blue")

# Plot individual points
for n in range(len(x)):
    # Vector to the point
    v = np.array([x[n]-x[p1], y[n]-y[p1], z[n]-z[p1]])

    # Projection to plane
    proj_plane = v - (np.dot(v, plane_normal)/plane_norm**2)*plane_normal 
    # print(proj_plane)

    # Its norm
    v_norm = np.sqrt(sum(v**2))

    x_proj.append(v_norm/ax_norm)

    color = "red" if ins[n] == False else "green"

    # Plot the point
    plt.plot(x_proj[n], rad[n], marker="o", color=color)
    
    # Plot line to previous point
    # if (n > 0):
        # plt.plot(x_proj[n-1], rad[n-1], x_proj[n]-x_proj[n-1], rad[n]-rad[n-1], color="red")
    
    # Annotate the current node
    plt.text(x_proj[n]+0.01, rad[n]+10, nod[n][-6:], fontsize="x-small")

ax.set_xlabel("projected position [-]")
ax.set_ylabel("altitude [km]")

# Set axis liimts
ax.set_xlim([-0.1, 1.1])
ax.set_ylim(min(rad)-150, max(rad)+150)

axis_labels = ax.get_yticks().tolist()
axis_labels_upd = [(x-6371000)/1000 for x in axis_labels]

ax.set_yticklabels(axis_labels_upd)

# Save plot
fig.savefig("plots/tracking_dbg/" + file + ".png", dpi=300)

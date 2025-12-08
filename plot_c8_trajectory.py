import matplotlib.pyplot as plt
import numpy as np
import os
from skspatial.objects import Line, Point
from skspatial.plotting import plot_2d
from math import sqrt

# Open logfile
with open("data/log.txt", "r") as log:
    content = log.readlines()
    # print(content)

# Atmosphere layers
atmo = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,34,36,38,40,42,44,46,48,50,55,60,65,70,75,80,85,90,95,100,110,115,120]

n_pt = 0
x = []
y = []
z = []
rad = []
nod = []
ins = []

for line in content:
    if "Tracking pos" in line:
        n_pt += 1
        print("New point [", n_pt, "]:", sep="")
        pos = line[line.index("(")+1:line.index(")")]
        print("  pos    :", pos)
        x.append(float(pos.split()[0]))
        y.append(float(pos.split()[1]))
        z.append(float(pos.split()[2]))
        radius = sqrt(x[-1]**2 + y[-1]**2 + z[-1]**2)
        rad.append(radius)
        print("  radius :", radius)
        print("  alt    :", radius-6371000)

    if "volumeNode=" in line:
        node = line[line.index("=")+1:line.index(",")]
        print("  node   :", node)
        nod.append(node)
        inside = line.rstrip()[line.rindex("=")+1:]
        print("  inside :", inside)
        inside_bool = True if inside == "true" else False
        ins.append(inside_bool)

proj_x = []
fig, ax = plt.subplots()

# Find furthest point from the first one
max_dist = 0
p1 = 0
p2 = 0
for n in range(len(x)):
    for m in range(len(x)):
        v = np.array([x[m]-x[n], y[m]-y[n], z[m]-z[n]])
        v_norm = np.sqrt(sum(v**2))
        if (v_norm > max_dist):
            print("Largest distance for", m, "and", n,":",v_norm,sep="")
            max_dist = v_norm
            p1 = n
            p2 = m
        
print("Furthest two points: ", p1, p2)

axis = np.array([x[p2]-x[p1], y[p2]-y[p1], z[p2]-z[p1]])
a_norm = np.sqrt(sum(axis**2))

# exit(0)
for n in range(len(x)):
    v = np.array([x[n]-x[p1], y[n]-y[p1], z[n]-z[p1]])
    
    # norm
    v_norm = np.sqrt(sum(v**2))

    # projection
    v_proj = (np.dot(axis, v)/v_norm**2)*v

    print("projection is ", v_proj)
    print("projection norm is ", v_norm/a_norm)
    
    plt.plot(v_norm/a_norm, rad[n], marker="o")

    plt.text(v_norm/a_norm, rad[n], nod[n])

# ax.add_patch(circ)
ax.set_xlim([-0.2, 1.2])
ax.set_ylim(min(rad)-5000, max(rad)+5000)

# exit(0)


# print("axis is", axis)
# for n in range(len(x)):
#     v = np.array([x[n]-x[0], y[n]-y[0], z[n]-z[0]])

#     rad = np.sqrt(x[n]**2 + y[n]**2 + z[n]**2)
    
#     # norm
#     v_norm = np.sqrt(sum(v**2))

#     # projection
#     v_proj = (np.dot(axis, v)/v_norm**2)*v

#     print("projection is ", v_proj)
#     print("projection norm is ", v_norm/a_norm)

#     plt.plot(v_norm/a_norm, rad, marker="o")

#     if n > 1:
#         plt.plot()

# Projection of earth center
v = np.array([-x[0], -y[0], -z[0]])
v_norm = np.sqrt(sum(v**2))

print("earth center norm is ", v_norm/a_norm)
for r in atmo:
    circ = plt.Circle((v_norm/a_norm, 0), r*1000+6371000, fill=False, color='blue')
    ax.add_patch(circ)


plt.show()

exit(0)

u = np.array([1, 2, 3])   # vector u
v = np.array([5, 6, 2])   # vector v:

# Task: Project vector u on vector v

# finding norm of the vector v
v_norm = np.sqrt(sum(v**2))    

# Apply the formula as mentioned above
# for projecting a vector onto another vector
# find dot product using np.dot()
proj_of_u_on_v = (np.dot(u, v)/v_norm**2)*v

print("Projection of Vector u on Vector v is: ", proj_of_u_on_v)

exit(0)

radius = 5000

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# for p in points:
ax.scatter(x, y, z, marker="o")

theta = np.linspace(0, 2 * np.pi, 100)
phi = np.linspace(0, np.pi, 50)
theta, phi = np.meshgrid(theta, phi)
r = 50000 + 6371000
# Convert to Cartesian coordinates
rx = r * np.sin(phi) * np.cos(theta)
ry = r * np.sin(phi) * np.sin(theta)
rz = r * np.cos(phi)



# ax.plot_surface(rx, ry, rz, cmap='viridis', alpha=0.8)
# ax.set_aspect('equal')

plt.show()

# fig.savefig("plots/tracking_dbg/1.png", dpi=300)


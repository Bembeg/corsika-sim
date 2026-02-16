#!/usr/bin/python3

import pandas as pd
import os
from matplotlib import pyplot as plt


# load test outputs
path = "data/atmo_tests.txt"

# open input file
with open(path, "r") as in_file:
    # get file content
    in_content = in_file.readlines()

# create temp files for processed test results
path_dens = "data/csv_dens.txt"
path_gram = "data/csv_gram.txt"
path_arclen = "data/csv_arclen.txt"

with open(path_dens, "w") as csv_dens:
    csv_dens.write("alt,diff\n")
    
    with open(path_gram, "w") as csv_gram:
        csv_gram.write("pass,downward,alt0,alt1,len,ang,diff\n")

        with open(path_arclen, "w") as csv_arclen:
            csv_arclen.write("pass,downward,alt0,alt1,len,ang,diff\n")

            for line in in_content:
                line_split = line.strip().split()

                # parse density results
                if "Dens:" in line:
                    # get altitude
                    alt = line_split[5]
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_dens.write(",".join([alt,diff]) + "\n")

                # parse integrated grammage results
                if "Gram:" in line:
                    # get pass status
                    passed = "1" if line_split[2] == "[pass]" else "0"
                    # track direction                    
                    downward = "1" if line_split[4] == "do" else "0"
                    # track endpoint altitudes
                    alt0 = line_split[7]
                    alt1 = line_split[10]
                    # track length
                    track_len = line_split[12].strip("(")
                    # track inclination
                    ang = line_split[16].strip("):")
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_gram.write(",".join([passed,downward,alt0,alt1,track_len,ang,diff]) + "\n")

                # parse arclength results
                if "Arclen:" in line:
                    # get pass status
                    passed = "1" if line_split[2] == "[pass]" else "0"
                    # track direction                    
                    downward = "1" if line_split[4] == "do" else "0"
                    # track endpoint altitudes
                    alt0 = line_split[7]
                    alt1 = line_split[10]
                    # track length
                    track_len = line_split[12].strip("(")
                    # track inclination
                    ang = line_split[16].strip("):")
                    # test diff
                    diff = line_split[-1]
                    # write to file
                    csv_arclen.write(",".join([passed,downward,alt0,alt1,track_len,ang,diff]) + "\n")

# Load created csv files as dataframes
df_dens = pd.read_csv(path_dens)
df_gram = pd.read_csv(path_gram)
df_arclen = pd.read_csv(path_arclen)

print(df_dens)
print(df_gram)
print(df_arclen)


os.makedirs("plots/atmo_tests", exist_ok=True)

# -----------------
# ---- DENSITY ----
# -----------------

fig, ax = plt.subplots()
df_dens.plot(x="alt", y="diff", title="density", xlabel="altitude [m]", ylabel="tab/ref - 1", legend=None, ax=ax)
ax.grid(ls="dashed", c="0.85")
fig.savefig("plots/atmo_tests/density.png", dpi=300)


# ------------------
# ---- GRAMMAGE ----
# ------------------

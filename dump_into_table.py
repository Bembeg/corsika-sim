#!/usr/bin/python

inpath ="data/USStdBK_full.csv"

outpath = "data/atmprof_USStdBK.dat"

alts = list(range(0, 115000, 1000))
alts += list(range(10000, 12000, 100))
alts += list(range(35000, 39000, 100))
alts += list(range(90000, 100000, 100))
alts += list(range(99800, 100010, 1))
alts += [112800]

with open(inpath, "r") as infile:
    content = infile.readlines()

with open(outpath, "w") as outfile:
    outfile.write("# alt[km]    rho[g/cm^3]    thick[g/cm^2]\n")

    for line in content:
        if "#" in line:
            continue

        line = line.strip()

        alt = int(line.split(",")[0])

        if alt in alts:
            # print(alt/1000, "\t", line.split(",")[1], "\t", line.split(",")[2])
            outfile.write(str(alt/1000))
            outfile.write(" " * (8 + 5 - len(str(alt/1000))))
            outfile.write(line.split(",")[1])
            outfile.write("    ")
            outfile.write(line.split(",")[2])
            outfile.write("\n")

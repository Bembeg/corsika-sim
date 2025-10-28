#!/usr/bin/python3
# Process call annotations and plot top N functions for multiple repetitions

from typing import NamedTuple
import matplotlib.pyplot as plt
import os

# Class to hold function cost (cst), function name (fn) and its corresponding library (lib)
class Result(NamedTuple):
    cst: float
    fn: str
    lib: str


# Make directory for plots
os.makedirs("plots")

# Iterate over callgrind annotate outputs
for sim in os.listdir("output/"):
    print("Dir", sim)

    output = "output/" + sim + "/annotate.txt"

    print("Processing output '", output, "'", sep="")

    # Open output file and read lines
    with open(output, "r") as f:
        lines = [line for line in f]

    # Run counter
    run = -1

    # Array to hold results
    results = []

    for line in lines:
        if ("TOTALS" in line):
            run += 1
            results.append([])
            continue

        if ("=" in line) or (len(line) < 5):
            continue

        # Parse cost
        cst = float(line[line.find("(")+1 : line.find(")")-1].strip())

        # Parse lib name
        if (line.find("[") == -1):
            lib = "-"
        else:
            lib = line[line.rfind("/")+1 : line.find("]")].strip()

        # Parse function name
        fn = line[line.find(")")+1 : line.find("[")].strip()
        if (fn.find("(") > 0):
            fn = fn[fn.rfind("/")+1 : fn.rfind("(")]
        else:
            fn = fn[fn.rfind("/")+1 :]

        result = Result(cst, fn, lib)

        # Result object to the array
        results[run].append(result)

    # Count runs and top functions
    n_runs = run+1
    n_fct = len(results[0])
    print(" - processed", n_runs, "runs, each with", n_fct, "functions")

    # Check if all rankings are identical
    print(" - checking if rankings match across runs")

    # Number of mismatches
    mismatch = 0

    for f in range(round(n_fct/2)):
        ref_f = results[0][f].fn
        for r in range(n_runs):
            # Detect diff between ref function (run0) and current function at the same position
            if (ref_f != results[r][f].fn):
                # print("    - diff in run ", r, ", pos ", f, " (ref: ", ref_f, ", curr: ", results[r][f].fn,")", sep="")
                mismatch += 1

    # Matching summary
    if (mismatch == 0):
        print(" - all rankings match\n")
    else:
        print(" - found", mismatch, "mismatch(es)\n")

    # Parse simulation label
    plot_name = output.split("/")[1]
    label = plot_name.replace("_prof", "").replace("pdg2212","proton").replace("pdg22","gamma")

    # Plot functions per run
    fig, ax = plt.subplots()
    # Plot size
    fig.set_figwidth(5)
    fig.set_figheight(5)
    fig.tight_layout(rect=[0.03, 0.35, 0.97, 0.97])
    # Axis labels and title
    ax.set_xlabel("n-th costliest function")
    ax.set_ylabel("function cost [%]")
    ax.set_title(label)
    # X-axis ticks
    ax.set(xticks=range(1, n_runs+1))
    # Grid
    ax.grid(True, linestyle="dashed", linewidth=0.5)

    # Plot individual runs
    for r in range(n_runs):
        # Collect costs and names of functions
        cst = [fct.cst for fct in results[r]]
        fct = [fct.fn for fct in results[r]]
        # Plot this run
        ax.plot(range(1, len(cst)+1), cst, label="run"+str(r)+" ("+str(round(sum(cst),1))+"%)", linewidth=1, linestyle="solid", marker="x")

    # List functions and corresponding libs
    for f in range(n_fct):
        ax.annotate(str(f+1) + ": " + results[0][f].fn[0:40] + "   [" + results[0][f].lib[0:30] + "]", (0.12, 0.30-f*0.03), xycoords="figure fraction", fontsize=8)

    # Draw legend
    ax.legend(fontsize=8)

    # Save plot
    plt.savefig("plots/" + plot_name + ".png", dpi=600)

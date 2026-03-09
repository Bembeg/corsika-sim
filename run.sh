#!/bin/bash
# Script for running Corsika8 simulations

print_usage() {
    echo "Usage:"
    echo "  Run simulations: ./$0 [suffix] [PID] [energy] [injHeight] [zenith] [nShowers] [nRuns]"
}

get_threads() {
    echo $(($(ps --no-headers -o pid --ppid=${MAIN_PID} | wc -w)-1))
}

keep_checking() {
    # Check if any child processes are still running
    while [ $(get_threads) -gt 0 ]; do
        echo -n "  Running PID: "

        # Output PIDs of still running processes
        for PID in ${RUNS[@]}; do
            if [[ $(ps --no-headers -p $PID | wc -l) -ne 0 ]]; then
                echo -n "$PID "
            fi
        done

        # Wait 5 seconds
        sleep 5

        # Clear line and carriage return
        echo -en "\033[2K\r"
    done

    # Clear line
    echo -en "\033[2K"
}

if [[ "$1" = "help" ]] || [[ "$1" = "-h" ]] || [[ "$1" = "--help" ]]; then
    print_usage
    exit 0
fi

# PID of the main process
MAIN_PID=$$

# Name suffix
SUF=$1
# Primary particle PDG code
PDG=$2
# Primary particle energy (in GeV)
ENE=$3
# Injection height (in m)
INJ=$4
# Zenith angle
ZEN=$5
# Number of showers in each run
NSHO=$6
# Number of runs
NRUN=$7

# Number of available threads
# THREADS=$(lscpu | grep "^CPU(s):" | grep -oE "[0-9]*")
THREADS=2

BUILD="release"

# Main directory with the Corsika project
MAIN_DIR="${PWD}/.."
# C8 executable
C8_EXEC="${MAIN_DIR}/corsika/install/${BUILD}/bin/c8_air_shower"
# Output directory
OUTPUT_DIR="${PWD}/output"

# Make output directory
mkdir -p ${OUTPUT_DIR}

# Enter C8 environment
source ${MAIN_DIR}/source.sh

echo "Shower simulation configuration:"

# Determine output directory name for this simulation
SIM_OUTPUT="${OUTPUT_DIR}/pdg${PDG}_E${ENE}_inj${INJ}_z${ZEN}_${SUF}"
echo " - PDG     :  $PDG"
echo " - Energy  :  $ENE"
echo " - Inj. H  :  $INJ"
echo " - Zenith  :  $ZEN"
echo " - Showers :  $NSHO"
echo " - Runs    :  $NRUN"
echo " - Suffix  :  $SUF"
echo " - Output  :  ${SIM_OUTPUT}"

for N in $(seq 0 1 $((NRUN-1))); do
    echo -en "\033[2K\rRunning: $((N+1))/$NRUN"

    RUN_OUTPUT=${SIM_OUTPUT}/run_$N

    # Check if output directory exists for this simulation
    if [ -d ${RUN_OUTPUT} ]; then
        # rm -rf ${RUN_OUTPUT}
        continue
    fi

    # Run Corsika
    ${C8_EXEC} \
        --nevent $NSHO \
        --pdg $PDG \
        -E $ENE \
        -f ${RUN_OUTPUT} \
        --disable-interaction-histograms \
        -s $((N+1)) \
        --injection-height $INJ \
        -z $ZEN \
        &> ${SIM_OUTPUT}_${N}.log &

        # --max-deflection-angle 0.02 \

    # Get PID of the new process
    PID=$!
    RUNS+=($PID)

    # Wait after starting a simulation run
    sleep 0.1

    # Keep waiting until some threads are free
    while [ $(get_threads) -ge $THREADS ]; do
        sleep 1
    done
done

# Newline
echo

echo "Waiting for simulations to finish"

# Wait for all simulations to finish
wait

echo -e "All done\n"

# Move log files into the respective output directories
for N in $(seq 0 1 $((NRUN-1))); do
    mv ${SIM_OUTPUT}_${N}.log ${SIM_OUTPUT}/run_$N/run.log 2>/dev/null
done

# Clean up leftover files from the run
rm -f .timer.out fort.*

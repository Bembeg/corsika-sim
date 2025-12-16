#!/bin/bash
# Script for running Corsika8 simulations

print_usage() {
    echo "Usage:"
    echo "  Run simulations: ./$0 [suffix]"
    echo "  Run and profile: ./$0 [suffix] --profile"
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

        # Clear line and Carriage return
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

# Suffix
SUF=$1

# Number of available threads
# THREADS=$(lscpu | grep "^CPU(s):" | grep -oE "[0-9]*")
THREADS=4

BUILD="rel"

# Main directory with the Corsika project
MAIN_DIR="${PWD}/.."
# C8 executable
C8_EXEC="${MAIN_DIR}/corsika/install/rel/bin/c8_air_shower"
# Output directory
OUTPUT_DIR="${PWD}/output"

# Make output directory
mkdir -p ${OUTPUT_DIR}

# Enter C8 environment
source ${MAIN_DIR}/setup.sh

# Particles to simulate - 22=gamma, 2212=proton
PARTICLES=(22)

# Primary energies to simulate (in GeV), corresponding to CTA energy range 20 GeV - 300 TeV
ENERGIES=(1)

# Number of showers in each simulation
SHOWERS=50

# Number of runs for each configuration
RUNS=1000

echo "Running shower simulations:"

# Run simulations
for PART in ${PARTICLES[@]}; do
    for ENE in ${ENERGIES[@]}; do
        # Determine output directory name for this simulation
        if [ "$1" = "--profile" ]; then
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}_${SUF}_prof"
        else 
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}_${SUF}"
        fi

        for N in $(seq 0 1 $((RUNS-1))); do
            echo -en "\033[2K\r    Primary particle PDG: $PART, energy: $ENE GeV, running $((N+1))/$RUNS"

            RUN_OUTPUT=${SIM_OUTPUT}/run_$N

            # Check if output directory exists for this simulation
            if [ -d ${RUN_OUTPUT} ]; then
                # echo "  Simulation output already exists for Primary particle PDG: $PART, energy: $ENE GeV"
                rm -rf ${RUN_OUTPUT}    
                # continue
            fi

            if [ "$1" = "--profile" ]; then
                # Run Corsika with valgrind profiling
                valgrind --tool=callgrind --callgrind-out-file=${SIM_OUTPUT}_${N}.prof --cache-sim=no \
                    ${C8_EXEC} \
                        --nevent $SHOWERS \
                        --pdg $PART \
                        -E $ENE \
                        -f ${RUN_OUTPUT} \
                        &> ${SIM_OUTPUT}_${N}.log &
            else      
                # Run Corsika
                ${C8_EXEC} \
                    --nevent $SHOWERS \
                    --pdg $PART \
                    -E $ENE \
                    -f ${RUN_OUTPUT} \
                    --disable-interaction-histograms \
                    &> ${SIM_OUTPUT}_${N}.log &
            fi

            # Get PID of the new process
            PID=$!
            RUNS+=($PID)
            
            # Profiling using Perf
            # sudo perf record -p $PID -F 999 -g -o ${RUN_OUTPUT}.data &

            # Wait after starting a simulation run
            sleep 0.1

            # Keep waiting until some threads are free
            while [ $(get_threads) -ge $THREADS ]; do
                sleep 1
            done
        done

        # Newline
        echo
    done
done

echo "Waiting for simulations to finish"

# Keep checking running processes
# keep_checking

# Wait for all simulations to finish
wait

echo "All done"

# Move log files into the respective output directories and print runtimes
# echo "Runtimes:"
for PART in ${PARTICLES[@]}; do
    for ENE in ${ENERGIES[@]}; do
        # Determine output directory name for this simulation
        if [ "$1" = "--profile" ]; then
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}_${SUF}_prof"
        else 
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}_${SUF}"
        fi

        for N in $(seq 0 1 $((RUNS-1))); do
            mv ${SIM_OUTPUT}_${N}.prof ${SIM_OUTPUT}/run_$N/run.prof 2>/dev/null
            mv ${SIM_OUTPUT}_${N}.log ${SIM_OUTPUT}/run_$N/run.log 2>/dev/null
            # echo "  PDG: $PART, energy: $ENE, $(cat ${RUN_OUTPUT}/summary.yaml | grep "runtime:")"
        done
    done
done

# Clean up leftover files from the run
rm -f .timer.out fort.*

exit 0

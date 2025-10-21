#!/bin/bash
# Script for running Corsika8 simulations

print_usage() {
    echo "Usage:"
    echo "  Run simulations: ./$0"
    echo "  Run and profile: ./$0 --profile"
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

# Number of available threads
THREADS=$(lscpu | grep "^CPU(s):" | grep -oE "[0-9]*")
THREADS=1

# Main directory with the Corsika project
MAIN_DIR="/scratch/home/rprivara/Corsika"
# C8 executable
C8_EXEC="${MAIN_DIR}/corsika/install/bin/c8_air_shower"
# Output directory
OUTPUT_DIR="${MAIN_DIR}/sim/output"

# Enter C8 environment
source ${MAIN_DIR}/setup.sh

# Particles to simulate - 22=gamma, 2212=proton
PARTICLES=(2212 22)

# Primary energies to simulate (in GeV), corresponding to CTA energy range 20 GeV - 300 TeV
#ENERGIES=(20 1000 300000)
ENERGIES=(20 1000 100000)

# Number of shower repetitions for each configuration
REPS=1

echo "Running shower simulations:"

# Run simulations
for PART in ${PARTICLES[@]}; do
    for ENE in ${ENERGIES[@]}; do
        # Determine output directory name for this simulation
        if [ "$1" = "--profile" ]; then
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}_prof"
        else 
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}"
        fi

        # Check if output directory exists for this simulation
        if [ -d ${SIM_OUTPUT} ]; then
            echo "  Simulation output already exists for Primary particle PDG: $PART, energy: $ENE GeV"

            rm -rf ${SIM_OUTPUT}
    
            # continue
        fi

        if [ "$1" = "--profile" ]; then
            # Run Corsika with valgrind profiling
            valgrind --tool=callgrind --callgrind-out-file=${SIM_OUTPUT}.profile \
                ${C8_EXEC} \
                    --nevent 1 \
                    --pdg $PART \
                    -E $ENE \
                    -f ${SIM_OUTPUT} \
                    &> ${SIM_OUTPUT}.log &
        else      
            # Run Corsika
            ${C8_EXEC} \
                --nevent 1 \
                --pdg $PART \
                -E $ENE \
                -f ${SIM_OUTPUT} \
                &> ${SIM_OUTPUT}.log &
        fi

        # Get PID of the new process
        PID=$!
        RUNS+=($PID)
        
        echo "  [PID:$PID] Primary particle PDG: $PART, energy: $ENE GeV"

        # Profiling using Perf
        # sudo perf record -p $PID -F 999 -g -o ${SIM_OUTPUT}.data &

        while [ get_threads -ge $THREADS ]; do
            echo "Waiting for available threads ($THREADS used)"
            sleep 1
        done
    done
done

echo "Waiting for simulations to finish"

# Keep checking running processes
keep_checking

# Probably unnecessary to also wait
wait

echo "All done"

# Move log files into the respective output directories and print runtimes
echo "Runtimes:"
for PART in ${PARTICLES[@]}; do
    for ENE in ${ENERGIES[@]}; do
        # Determine output directory name for this simulation
        if [ "$1" = "--profile" ]; then
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}_prof"
            mv ${SIM_OUTPUT}.profile ${SIM_OUTPUT}/run.profile
        else 
            SIM_OUTPUT="${OUTPUT_DIR}/pdg${PART}_E${ENE}"
        fi

        mv ${SIM_OUTPUT}.log ${SIM_OUTPUT}/run.log 2>/dev/null
        echo "  PDG: $PART, energy: $ENE, $(cat ${SIM_OUTPUT}/summary.yaml | grep "runtime:")"
    done
done

# Clean up leftover files from the run
rm -f .timer.out fort.*

exit 0

source ../source.sh

# Run simulations
if true; then
    CONFIG="opt_interp_v1"
    bash run.sh $CONFIG 2212 1e3 112750 0 1 1000
    bash run.sh $CONFIG 2212 1e3 80000 60 1 1000
fi

# Merge outputs
if true; then
    # reference exponential model
    python3 merge_outputs.py pdg2212_E1e3_inj112750_z0_opt_expon
    python3 merge_outputs.py pdg2212_E1e3_inj80000_z60_opt_expon

    # reference interpolated model (MR branch)
    python3 merge_outputs.py pdg2212_E1e3_inj112750_z0_opt_interp_ref
    python3 merge_outputs.py pdg2212_E1e3_inj80000_z60_opt_interp_ref

    # v1 is using arrays and 250000 lookup entries
    # python3 merge_outputs.py pdg2212_E1e3_inj112750_z0_opt_interp_v1
    # python3 merge_outputs.py pdg2212_E1e3_inj80000_z60_opt_interp_v1

fi

# Analysis
if true; then
    python3 analysis.py opt_z0  pdg2212_E1e3_inj112750_z0_opt_interp_ref pdg2212_E1e3_inj112750_z0_opt_expon # pdg2212_E1e3_inj112750_z0_opt_interp_v1
    python3 analysis.py opt_z60 pdg2212_E1e3_inj80000_z60_opt_interp_ref pdg2212_E1e3_inj80000_z60_opt_expon # pdg2212_E1e3_inj80000_z60_opt_interp_v1
fi

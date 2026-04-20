source ../source.sh

# Run simulations
if true; then
    CONFIG="opt_interp_v6"
    bash run.sh $CONFIG 2212 1e4 112750 0 1 10
    bash run.sh $CONFIG 2212 1e4 80000 60 1 10
fi

# Merge outputs
if true; then
    echo
    
    # reference exponential model
    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_expon
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_expon

    # # reference interpolated model (MR branch)
    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_ref
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_ref

    # # v1 is using arrays and 250000 lookup entries, index diff in getArclen changed 3->1
    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_v1
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_v1

    # # v2
    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_v2
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_v2

    # # v3
    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_v3
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_v3

    # v3
    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_v4
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_v4

    # python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_v5
    # python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_v5

    python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_opt_interp_v6
    python3 merge_outputs.py pdg2212_E1e4_inj80000_z60_opt_interp_v6
fi

# Analysis
if true; then
    python3 analysis.py opt_z0 \
        pdg2212_E1e4_inj112750_z0_opt_expon \
        pdg2212_E1e4_inj112750_z0_opt_interp_ref \
        pdg2212_E1e4_inj112750_z0_opt_interp_v3 \
        pdg2212_E1e4_inj112750_z0_opt_interp_v4 \
        pdg2212_E1e4_inj112750_z0_opt_interp_v5 \
        pdg2212_E1e4_inj112750_z0_opt_interp_v6

    python3 analysis.py opt_z60 \
        pdg2212_E1e4_inj80000_z60_opt_expon \
        pdg2212_E1e4_inj80000_z60_opt_interp_ref \
        pdg2212_E1e4_inj80000_z60_opt_interp_v4 \
        pdg2212_E1e4_inj80000_z60_opt_interp_v5 \
        pdg2212_E1e4_inj80000_z60_opt_interp_v6

fi

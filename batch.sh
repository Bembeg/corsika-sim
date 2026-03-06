source ../source.sh

# Run simulations
if true; then
    CONFIG="interp"
    # Standard injection height
    bash run.sh $CONFIG 22 1e3 112750 0 1 1000
    bash run.sh $CONFIG 22 1e4 112750 0 1 500
    bash run.sh $CONFIG 22 1e5 112750 0 1 100
    bash run.sh $CONFIG 2212 1e3 112750 0 1 1000
    bash run.sh $CONFIG 2212 1e4 112750 0 1 500
    bash run.sh $CONFIG 2212 1e5 112750 0 1 100
    # Low injection height
    bash run.sh $CONFIG 22 1e3 6900 0 1 1000
    bash run.sh $CONFIG 22 1e4 6900 0 1 500
    bash run.sh $CONFIG 22 1e5 6900 0 1 100
    bash run.sh $CONFIG 2212 1e3 6900 0 1 1000
    bash run.sh $CONFIG 2212 1e4 6900 0 1 500
    bash run.sh $CONFIG 2212 1e5 6900 0 1 100
fi

# Merge outputs
if true; then
    # Standard injection height
    python3 merge_outputs.py pdg22_E1e3_inj112750_z0_interp
    python3 merge_outputs.py pdg22_E1e4_inj112750_z0_interp
    python3 merge_outputs.py pdg22_E1e5_inj112750_z0_interp
    python3 merge_outputs.py pdg2212_E1e3_inj112750_z0_interp
    python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_interp
    python3 merge_outputs.py pdg2212_E1e5_inj112750_z0_interp
    python3 merge_outputs.py pdg22_E1e3_inj112750_z0_expon
    python3 merge_outputs.py pdg22_E1e4_inj112750_z0_expon
    python3 merge_outputs.py pdg22_E1e5_inj112750_z0_expon
    python3 merge_outputs.py pdg2212_E1e3_inj112750_z0_expon
    python3 merge_outputs.py pdg2212_E1e4_inj112750_z0_expon
    python3 merge_outputs.py pdg2212_E1e5_inj112750_z0_expon
    # Low injection height
    python3 merge_outputs.py pdg22_E1e3_inj6900_z0_interp
    python3 merge_outputs.py pdg22_E1e4_inj6900_z0_interp
    python3 merge_outputs.py pdg22_E1e5_inj6900_z0_interp
    python3 merge_outputs.py pdg2212_E1e3_inj6900_z0_interp
    python3 merge_outputs.py pdg2212_E1e4_inj6900_z0_interp
    python3 merge_outputs.py pdg2212_E1e5_inj6900_z0_interp
    python3 merge_outputs.py pdg22_E1e3_inj6900_z0_expon
    python3 merge_outputs.py pdg22_E1e4_inj6900_z0_expon
    python3 merge_outputs.py pdg22_E1e5_inj6900_z0_expon
    python3 merge_outputs.py pdg2212_E1e3_inj6900_z0_expon
    python3 merge_outputs.py pdg2212_E1e4_inj6900_z0_expon
    python3 merge_outputs.py pdg2212_E1e5_inj6900_z0_expon
fi

# Analysis
if true; then
    # Standard injection height
    python3 analysis.py pdg22_E1e3_stdAlt pdg22_E1e3_inj112750_z0_expon pdg22_E1e3_inj112750_z0_interp
    python3 analysis.py pdg22_E1e4_stdAlt pdg22_E1e4_inj112750_z0_expon pdg22_E1e4_inj112750_z0_interp
    python3 analysis.py pdg22_E1e5_stdAlt pdg22_E1e5_inj112750_z0_expon pdg22_E1e5_inj112750_z0_interp
    python3 analysis.py pdg2212_E1e3_stdAlt pdg2212_E1e3_inj112750_z0_expon pdg2212_E1e3_inj112750_z0_interp
    python3 analysis.py pdg2212_E1e4_stdAlt pdg2212_E1e4_inj112750_z0_expon pdg2212_E1e4_inj112750_z0_interp
    python3 analysis.py pdg2212_E1e5_stdAlt pdg2212_E1e5_inj112750_z0_expon pdg2212_E1e5_inj112750_z0_interp
    # Low injection height
    python3 analysis.py pdg22_E1e3_lowAlt pdg22_E1e3_inj6900_z0_expon pdg22_E1e3_inj6900_z0_interp
    python3 analysis.py pdg22_E1e4_lowAlt pdg22_E1e4_inj6900_z0_expon pdg22_E1e4_inj6900_z0_interp
    python3 analysis.py pdg22_E1e5_lowAlt pdg22_E1e5_inj6900_z0_expon pdg22_E1e5_inj6900_z0_interp
    python3 analysis.py pdg2212_E1e3_lowAlt pdg2212_E1e3_inj6900_z0_expon pdg2212_E1e3_inj6900_z0_interp
    python3 analysis.py pdg2212_E1e4_lowAlt pdg2212_E1e4_inj6900_z0_expon pdg2212_E1e4_inj6900_z0_interp
    python3 analysis.py pdg2212_E1e5_lowAlt pdg2212_E1e5_inj6900_z0_expon pdg2212_E1e5_inj6900_z0_interp
fi

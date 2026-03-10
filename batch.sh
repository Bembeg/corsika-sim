source ../source.sh

# Run simulations
if true; then
    CONFIG="interp"
    bash run.sh $CONFIG 2212 1e3 112750 60 1 1000
    bash run.sh $CONFIG 2212 1e4 112750 60 1 1000
    bash run.sh $CONFIG 2212 1e5 112750 60 1 500
fi

# Merge outputs
if false; then
    python3 merge_outputs.py pdg2212_E1e3_inj112750_z60_interp
    python3 merge_outputs.py pdg2212_E1e4_inj112750_z60_interp
    python3 merge_outputs.py pdg2212_E1e5_inj112750_z60_interp
    python3 merge_outputs.py pdg2212_E1e3_inj112750_z60_expon
    python3 merge_outputs.py pdg2212_E1e4_inj112750_z60_expon
    python3 merge_outputs.py pdg2212_E1e5_inj112750_z60_expon
fi

# Analysis
if false; then
    python3 analysis.py pdg2212_E1e3_incl pdg2212_E1e3_inj112750_z60_expon pdg2212_E1e3_inj112750_z60_interp
    python3 analysis.py pdg2212_E1e4_incl pdg2212_E1e4_inj112750_z60_expon pdg2212_E1e4_inj112750_z60_interp
    python3 analysis.py pdg2212_E1e5_incl pdg2212_E1e5_inj112750_z60_expon pdg2212_E1e5_inj112750_z60_interp
fi

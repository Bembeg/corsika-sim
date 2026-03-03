source ../source.sh

# Run simulations
CONFIG="interp"
# Standard injection height
bash run.sh $CONFIG 22 1e3 112750 0 1 10
bash run.sh $CONFIG 22 1e4 112750 0 1 10
bash run.sh $CONFIG 22 1e5 112750 0 1 2
bash run.sh $CONFIG 2212 1e3 112750 0 1 10
bash run.sh $CONFIG 2212 1e4 112750 0 1 10
bash run.sh $CONFIG 2212 1e5 112750 0 1 2
# Low injection height
bash run.sh $CONFIG 22 1e3 6900 0 1 10
bash run.sh $CONFIG 22 1e4 6900 0 1 10
bash run.sh $CONFIG 22 1e5 6900 0 1 2
bash run.sh $CONFIG 2212 1e3 6900 0 1 10
bash run.sh $CONFIG 2212 1e4 6900 0 1 10
bash run.sh $CONFIG 2212 1e5 6900 0 1 2

# Merge outputs
if false; then
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
if false; then
    # Standard injection height
    python3 pdg22_E1e3_stdAlt pdg22_E1e3_inj112750_z0_expon pdg22_E1e3_inj112750_z0_interp
    python3 pdg22_E1e4_stdAlt pdg22_E1e4_inj112750_z0_expon pdg22_E1e4_inj112750_z0_interp
    python3 pdg22_E1e5_stdAlt pdg22_E1e5_inj112750_z0_expon pdg22_E1e5_inj112750_z0_interp
    # Low injection height
    python3 pdg22_E1e3_lowAlt pdg22_E1e3_inj6900_z0_expon pdg22_E1e3_inj6900_z0_interp
    python3 pdg22_E1e4_lowAlt pdg22_E1e4_inj6900_z0_expon pdg22_E1e4_inj6900_z0_interp
    python3 pdg22_E1e5_lowAlt pdg22_E1e5_inj6900_z0_expon pdg22_E1e5_inj6900_z0_interp
fi

source ../source.sh

# Run simulations
if true; then
    CONFIG="cherOnFilt"
    bash run.sh $CONFIG 22 1e0 112750 0 1 1
    bash run.sh $CONFIG 22 1e1 112750 0 1 1
    bash run.sh $CONFIG 22 1e2 112750 0 1 1
    bash run.sh $CONFIG 22 1e3 112750 0 1 1
    bash run.sh $CONFIG 22 1e4 112750 0 1 1
    
    bash run.sh $CONFIG 22 1e0 112750 60 1 1
    bash run.sh $CONFIG 22 1e1 112750 60 1 1
    bash run.sh $CONFIG 22 1e2 112750 60 1 1
    bash run.sh $CONFIG 22 1e3 112750 60 1 1
    bash run.sh $CONFIG 22 1e4 112750 60 1 1
fi

# Merge outputs
if true; then
    python3 merge_outputs.py pdg22_E1e0_inj112750_z0_cherOff
    python3 merge_outputs.py pdg22_E1e1_inj112750_z0_cherOff
    python3 merge_outputs.py pdg22_E1e2_inj112750_z0_cherOff
    python3 merge_outputs.py pdg22_E1e3_inj112750_z0_cherOff
    python3 merge_outputs.py pdg22_E1e4_inj112750_z0_cherOff
    python3 merge_outputs.py pdg22_E1e0_inj112750_z40_cherOff
    python3 merge_outputs.py pdg22_E1e1_inj112750_z40_cherOff
    python3 merge_outputs.py pdg22_E1e2_inj112750_z40_cherOff
    python3 merge_outputs.py pdg22_E1e3_inj112750_z40_cherOff
    python3 merge_outputs.py pdg22_E1e4_inj112750_z40_cherOff

    python3 merge_outputs.py pdg22_E1e0_inj112750_z0_cherOn
    python3 merge_outputs.py pdg22_E1e1_inj112750_z0_cherOn
    python3 merge_outputs.py pdg22_E1e2_inj112750_z0_cherOn
    python3 merge_outputs.py pdg22_E1e3_inj112750_z0_cherOn
    python3 merge_outputs.py pdg22_E1e4_inj112750_z0_cherOn
    python3 merge_outputs.py pdg22_E1e0_inj112750_z40_cherOn
    python3 merge_outputs.py pdg22_E1e1_inj112750_z40_cherOn
    python3 merge_outputs.py pdg22_E1e2_inj112750_z40_cherOn
    python3 merge_outputs.py pdg22_E1e3_inj112750_z40_cherOn
    python3 merge_outputs.py pdg22_E1e4_inj112750_z40_cherOn

    python3 merge_outputs.py pdg22_E1e0_inj112750_z0_cherOnFilt
    python3 merge_outputs.py pdg22_E1e1_inj112750_z0_cherOnFilt
    python3 merge_outputs.py pdg22_E1e2_inj112750_z0_cherOnFilt
    python3 merge_outputs.py pdg22_E1e3_inj112750_z0_cherOnFilt
    python3 merge_outputs.py pdg22_E1e4_inj112750_z0_cherOnFilt
    python3 merge_outputs.py pdg22_E1e0_inj112750_z40_cherOnFilt
    python3 merge_outputs.py pdg22_E1e1_inj112750_z40_cherOnFilt
    python3 merge_outputs.py pdg22_E1e2_inj112750_z40_cherOnFilt
    python3 merge_outputs.py pdg22_E1e3_inj112750_z40_cherOnFilt
    python3 merge_outputs.py pdg22_E1e4_inj112750_z40_cherOnFilt

fi

# Analysis
if true; then
    python3 analysis.py cherOff_z0 \
        pdg22_E1e0_inj112750_z0_cherOff \
        pdg22_E1e1_inj112750_z0_cherOff \
        pdg22_E1e2_inj112750_z0_cherOff \
        pdg22_E1e3_inj112750_z0_cherOff \
        pdg22_E1e4_inj112750_z0_cherOff 
    
    python3 analysis.py cherOff_z40 \
        pdg22_E1e0_inj112750_z40_cherOff \
        pdg22_E1e1_inj112750_z40_cherOff \
        pdg22_E1e2_inj112750_z40_cherOff \
        pdg22_E1e3_inj112750_z40_cherOff \
        pdg22_E1e4_inj112750_z40_cherOff 

    python3 analysis.py cherOn_z0 \
        pdg22_E1e0_inj112750_z0_cherOn \
        pdg22_E1e1_inj112750_z0_cherOn \
        pdg22_E1e2_inj112750_z0_cherOn \
        pdg22_E1e3_inj112750_z0_cherOn \
        pdg22_E1e4_inj112750_z0_cherOn 
    
    python3 analysis.py cherOn_z40 \
        pdg22_E1e0_inj112750_z40_cherOn \
        pdg22_E1e1_inj112750_z40_cherOn \
        pdg22_E1e2_inj112750_z40_cherOn \
        pdg22_E1e3_inj112750_z40_cherOn \
        pdg22_E1e4_inj112750_z40_cherOn 

    python3 analysis.py cherOnFilt_z0 \
        pdg22_E1e0_inj112750_z0_cherOnFilt \
        pdg22_E1e1_inj112750_z0_cherOnFilt \
        pdg22_E1e2_inj112750_z0_cherOnFilt \
        pdg22_E1e3_inj112750_z0_cherOnFilt \
        pdg22_E1e4_inj112750_z0_cherOnFilt 
    
    python3 analysis.py cherOnFilt_z40 \
        pdg22_E1e0_inj112750_z40_cherOnFilt \
        pdg22_E1e1_inj112750_z40_cherOnFilt \
        pdg22_E1e2_inj112750_z40_cherOnFilt \
        pdg22_E1e3_inj112750_z40_cherOnFilt \
        pdg22_E1e4_inj112750_z40_cherOnFilt 
fi

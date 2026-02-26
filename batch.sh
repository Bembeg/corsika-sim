source ../source.sh

# python3 merge_outputs.py pdg2212_E1000_expon
# python3 merge_outputs.py pdg2212_E1000_interp
# python3 merge_outputs.py pdg22_E1000_expon
# python3 merge_outputs.py pdg22_E1000_interp

# python3 merge_outputs.py pdg2212_E10000_expon
# python3 merge_outputs.py pdg2212_E10000_interp
# python3 merge_outputs.py pdg22_E10000_expon
# python3 merge_outputs.py pdg22_E10000_interp

# python3 merge_outputs.py pdg2212_E100000_expon
# python3 merge_outputs.py pdg2212_E100000_interp

# python3 analysis.py pdg2212_E1000 pdg2212_E1000_expon pdg2212_E1000_interp
# python3 analysis.py pdg2212_E10000 pdg2212_E10000_expon pdg2212_E10000_interp
# python3 analysis.py pdg2212_E100000 pdg2212_E100000_expon pdg2212_E100000_interp

# python3 analysis.py pdg22_E1000 pdg22_E1000_expon pdg22_E1000_interp
# python3 analysis.py pdg22_E10000 pdg22_E10000_expon pdg22_E10000_interp

python3 merge_outputs.py pdg2212_E1e3_expon
python3 merge_outputs.py pdg2212_E1e3_interp
python3 merge_outputs.py pdg2212_E1e4_expon
python3 merge_outputs.py pdg2212_E1e4_interp
python3 merge_outputs.py pdg2212_E1e5_expon
python3 merge_outputs.py pdg2212_E1e5_interp

python3 analysis.py pdg2212_E1e3 pdg2212_E1e3_expon pdg2212_E1e3_interp
python3 analysis.py pdg2212_E1e4 pdg2212_E1e4_expon pdg2212_E1e4_interp
python3 analysis.py pdg2212_E1e5 pdg2212_E1e5_expon pdg2212_E1e5_interp

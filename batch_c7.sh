source ../source.sh

# run CORSIKA7 simulations
# [name] [showers] [prim] [energy] [azimuth] [zenith] [obs. level] [cherWavelenMin] [cherWavelenMax] [bunching]
# bash run_c7.sh gamma_E1e10_z0 1 1 10 0 0 214700 240 1000 5

# process simulation outputs
python3 plotEventIO.py output-c7/gamma_E1e10_z0/output.corsika

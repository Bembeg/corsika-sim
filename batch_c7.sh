source ../source.sh

# run CORSIKA7 simulations
if false; then
    # [name] [showers] [prim] [energy] [azimuth] [zenith] [obs. level] [cherWavelenMin] [cherWavelenMax] [bunching]
    bash run_c7.sh c7_gamma_E1e10_z0 1000 1 10 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e11_z0 1000 1 100 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z0 1000 1 1000 0 0 214700 240 1000 5
fi

# process simulation outputs
if false; then
    python3 -W ignore plotEventIO.py \
        gamma_z0 \
        output/c7_gamma_E1e10_z0 \
        output/c7_gamma_E1e11_z0
fi

# run converter from parquet to EventIO
if true; then
    python3 convert_parquet_eventio.py output/c8_gamma_E1e10_z0
fi

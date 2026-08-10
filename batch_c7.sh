source ../source.sh

# run CORSIKA 7 simulations
if true; then
    # [name] [showers] [prim] [energy] [azimuth] [zenith] [obs. level] [cherWavelenMin] [cherWavelenMax] [bunching]
    bash run_c7.sh c7_gamma_E1e10_z0 5000 1 10 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e11_z0 1000 1 100 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z0 250 1 1000 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e10_z20 5000 1 10 0 20 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e10_z40 5000 1 10 0 40 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e10_z60 5000 1 10 0 60 214700 240 1000 5
fi

# run CORSIKA 8 simulations
if true; then
    bash run.sh c8_gamma_E1e10_z0 22 10 119999.9 0 5000 1
    bash run.sh c8_gamma_E1e11_z0 22 100 119999.9 0 1000 1
    bash run.sh c8_gamma_E1e12_z0 22 1000 119999.9 0 250 1
    bash run.sh c8_gamma_E1e10_z20 22 10 119999.9 20 5000 1
    bash run.sh c8_gamma_E1e10_z40 22 10 119999.9 40 5000 1
    bash run.sh c8_gamma_E1e10_z60 22 10 119999.9 60 5000 1
fi

# run converter from parquet to EventIO
if false; then
    python3 convert_parquet_eventio.py output/c8_gamma_E1e10_z0 output/c8_gamma_E1e10_z0/output.corsika
fi

# process simulation outputs
if false; then
    python3 -W ignore plotEventIO.py c7_gamma_E1e10_z0 output/c7_gamma_E1e10_z0
    python3 -W ignore plotEventIO.py c8_gamma_E1e10_z0 output/c8_gamma_E1e10_z0

    python3 -W ignore plotEventIO.py \
        gamma_E1e10_z0 \
        output/c7_gamma_E1e10_z0 \
        output/c8_gamma_E1e10_z0
fi

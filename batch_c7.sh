source ../source.sh

# run CORSIKA 7 simulations
if false; then
    # [name] [showers] [prim] [energy] [azimuth] [zenith] [obs. level] [cherWavelenMin] [cherWavelenMax] [bunching]
    bash run_c7.sh c7_gamma_E1e12_z0 5000 1 1000 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z20 1000 1 1000 0 20 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z40 1000 1 1000 0 40 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z60 1000 1 1000 0 60 214700 240 1000 5

    # bash run_c7.sh c7_proton_E1e12_z0 1000 14 1000 0 0 214700 240 1000 5
    # bash run_c7.sh c7_proton_E1e12_z20 1000 14 1000 0 20 214700 240 1000 5
    # bash run_c7.sh c7_proton_E1e12_z40 1000 14 1000 0 40 214700 240 1000 5
    # bash run_c7.sh c7_proton_E1e12_z60 1000 14 1000 0 60 214700 240 1000 5
fi

# run CORSIKA 8 simulations
if false; then
    bash run.sh c8_gamma_E1e12_z0_v2 22 1000 119999.9 0 5000 1
    bash run.sh c8_gamma_E1e12_z20_v2 22 1000 119999.9 20 1000 1
    bash run.sh c8_gamma_E1e12_z40_v2 22 1000 119999.9 40 1000 1
    bash run.sh c8_gamma_E1e12_z60_v2 22 1000 119999.9 60 1000 1

    # bash run.sh c8_proton_E1e12_z0_v2 2212 1000 119999.9 0 1000 1
    # bash run.sh c8_proton_E1e12_z20_v2 2212 1000 119999.9 20 1000 1
    # bash run.sh c8_proton_E1e12_z40_v2 2212 1000 119999.9 40 1000 1
    # bash run.sh c8_proton_E1e12_z60_v2 2212 1000 119999.9 60 1000 1
fi

# run converter from parquet to EventIO
if false; then
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z0_v4
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z20_v4
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z40_v4
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z60_v4

    # python3 convert_parquet_eventio.py output/c8_proton_E1e12_z0_v2 output/c8_proton_E1e12_z0_v2/output.corsika
    # python3 convert_parquet_eventio.py output/c8_proton_E1e12_z20_v2 output/c8_proton_E1e12_z20_v2/output.corsika
    # python3 convert_parquet_eventio.py output/c8_proton_E1e12_z40_v2 output/c8_proton_E1e12_z40_v2/output.corsika
    # python3 convert_parquet_eventio.py output/c8_proton_E1e12_z60_v2 output/c8_proton_E1e12_z60_v2/output.corsika
fi

# process simulation outputs
if false; then
    python3 -W ignore plotEventIO.py gamma_E1e12_z0 output/c7_gamma_E1e12_z0 output/c8_gamma_E1e12_z0_v4
    python3 -W ignore plotEventIO.py gamma_E1e12_z20 output/c7_gamma_E1e12_z20 output/c8_gamma_E1e12_z20_v4
    python3 -W ignore plotEventIO.py gamma_E1e12_z40 output/c7_gamma_E1e12_z40 output/c8_gamma_E1e12_z40_v4
    python3 -W ignore plotEventIO.py gamma_E1e12_z60 output/c7_gamma_E1e12_z60 output/c8_gamma_E1e12_z60_v4

    # python3 -W ignore plotEventIO.py proton_E1e12_z0_v2 output/c7_proton_E1e12_z0 output/c8_proton_E1e12_z0_v2
    # python3 -W ignore plotEventIO.py proton_E1e12_z20_v2 output/c7_proton_E1e12_z20 output/c8_proton_E1e12_z20_v2
    # python3 -W ignore plotEventIO.py proton_E1e12_z40_v2 output/c7_proton_E1e12_z40 output/c8_proton_E1e12_z40_v2
    # python3 -W ignore plotEventIO.py proton_E1e12_z60_v2 output/c7_proton_E1e12_z60 output/c8_proton_E1e12_z60_v2
fi

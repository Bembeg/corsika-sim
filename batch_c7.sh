source ../source.sh

# run CORSIKA 7 simulations
if true; then
    # [name] [showers] [prim] [energy] [azimuth] [zenith] [obs. level] [cherWavelenMin] [cherWavelenMax] [bunching]
    bash run_c7.sh c7_gamma_E1e12_z0 1000 1 1000 0 0 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z20 1000 1 1000 0 20 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z40 1000 1 1000 0 40 214700 240 1000 5
    bash run_c7.sh c7_gamma_E1e12_z60 1000 1 1000 0 60 214700 240 1000 5

    bash run_c7.sh c7_proton_E1e12_z0 1000 14 1000 0 0 214700 240 1000 5
    bash run_c7.sh c7_proton_E1e12_z20 1000 14 1000 0 20 214700 240 1000 5
    bash run_c7.sh c7_proton_E1e12_z40 1000 14 1000 0 40 214700 240 1000 5
    bash run_c7.sh c7_proton_E1e12_z60 1000 14 1000 0 60 214700 240 1000 5
fi

# run CORSIKA 8 simulations
if true; then
    bash run.sh c8_gamma_E1e12_z0 22 1000 119999.9 0 1000 1
    bash run.sh c8_gamma_E1e12_z20 22 1000 119999.9 20 1000 1
    bash run.sh c8_gamma_E1e12_z40 22 1000 119999.9 40 1000 1
    bash run.sh c8_gamma_E1e12_z60 22 1000 119999.9 60 1000 1

    bash run.sh c8_proton_E1e12_z0 2212 1000 119999.9 0 1000 1
    bash run.sh c8_proton_E1e12_z20 2212 1000 119999.9 20 1000 1
    bash run.sh c8_proton_E1e12_z40 2212 1000 119999.9 40 1000 1
    bash run.sh c8_proton_E1e12_z60 2212 1000 119999.9 60 1000 1
fi

# run converter from parquet to EventIO
if true; then
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z0 output/c8_gamma_E1e12_z0/output.corsika
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z20 output/c8_gamma_E1e12_z20/output.corsika
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z40 output/c8_gamma_E1e12_z40/output.corsika
    python3 convert_parquet_eventio.py output/c8_gamma_E1e12_z60 output/c8_gamma_E1e12_z60/output.corsika

    python3 convert_parquet_eventio.py output/c8_proton_E1e12_z0 output/c8_proton_E1e12_z0/output.corsika
    python3 convert_parquet_eventio.py output/c8_proton_E1e12_z20 output/c8_proton_E1e12_z20/output.corsika
    python3 convert_parquet_eventio.py output/c8_proton_E1e12_z40 output/c8_proton_E1e12_z40/output.corsika
    python3 convert_parquet_eventio.py output/c8_proton_E1e12_z60 output/c8_proton_E1e12_z60/output.corsika
fi

# process simulation outputs
if true; then
    python3 -W ignore plotEventIO.py gamma_E1e12_z0 output/c7_gamma_E1e12_z0 output/c8_gamma_E1e12_z0
    python3 -W ignore plotEventIO.py gamma_E1e12_z20 output/c7_gamma_E1e12_z20 output/c8_gamma_E1e12_z20
    python3 -W ignore plotEventIO.py gamma_E1e12_z40 output/c7_gamma_E1e12_z40 output/c8_gamma_E1e12_z40
    python3 -W ignore plotEventIO.py gamma_E1e12_z60 output/c7_gamma_E1e12_z60 output/c8_gamma_E1e12_z60

    python3 -W ignore plotEventIO.py proton_E1e12_z0 output/c7_proton_E1e12_z0 output/c8_proton_E1e12_z0
    python3 -W ignore plotEventIO.py proton_E1e12_z20 output/c7_proton_E1e12_z20 output/c8_proton_E1e12_z20
    python3 -W ignore plotEventIO.py proton_E1e12_z40 output/c7_proton_E1e12_z40 output/c8_proton_E1e12_z40
    python3 -W ignore plotEventIO.py proton_E1e12_z60 output/c7_proton_E1e12_z60 output/c8_proton_E1e12_z60
fi

source ../source.sh

# get cherenkov parquet output file and config
cp -rf /scratch/home/rprivara/Corsika/corsika/build/debug/tests/modules/light* data/

# run plotting script
python3 plotCherenkov.py

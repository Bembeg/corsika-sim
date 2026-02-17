
source ../source.sh

# generate atmosphere
echo "Generating table"
python3 dump_into_table.py

# copy to C8
echo "Copying table to C8 codebase"
cp data/atmprof_USStdBK.dat ../corsika/tests/media/

# run test and produce output
echo "Running testAtmosphereTable"
../corsika/build/release/tests/media/testMedia > data/atmo_tests.txt

# run test analysis
echo "Running test result analysis"
python3 atmo_tests.py


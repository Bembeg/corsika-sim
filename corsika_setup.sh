mkdir -p build/debug build/release

THR=$(lscpu | grep "^CPU(s):" | grep -oE [0-9]*)

# Debug build
cd build/debug
../../conan-install.sh --source-directory ../.. --debug
../../corsika-cmake.sh -c "-DCMAKE_BUILD_TYPE="Debug" -DWITH_FLUKA=ON -DCMAKE_INSTALL_PREFIX=../../install/debug"
make install -j$THR
ctest -j$THR
TEST_DBG=$?
cd -

# Release build
cd build/release
../../conan-install.sh --source-directory ../.. --release
../../corsika-cmake.sh -c "-DCMAKE_BUILD_TYPE="Release" -DWITH_FLUKA=ON -DCMAKE_INSTALL_PREFIX=../../install/release"
make install -j$THR
ctest -j$THR
TEST_REL=$?
echo
cd -

echo "Test debug build: result $TEST_DBG"
echo "Test release build: result $TEST_REL"



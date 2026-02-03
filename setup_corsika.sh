WDIR=$(pwd)
THR=$(lscpu | grep "^CPU(s):" | grep -oE [0-9]*)
THR=6

# Virtual env
if [ ! -d $WDIR/corsika-env ]; then
	python3 -m venv $WDIR/corsika-env
	source $WDIR/corsika-env/bin/activate
	pip install conan particle==0.25.1 numpy sphinx
else
	echo "Virtual environment already set up"
fi

# Sourcing script
SCR=$WDIR/source.sh
rm -f $SCR && touch $SCR
echo "source "$WDIR/corsika-env/bin/activate"" >> $SCR
echo -e "export FLUFOR=\"gfortran\"" >> $SCR
echo -e "export FLUPRO=\"$WDIR/fluka\"" >> $SCR
source $SCR

# Setup fluka
if [ ! -f $WDIR/fluka/flukahp ]; then
	mkdir -p $WDIR/fluka && cd $WDIR/fluka
	rsync -avhP rprivara@lxplus.cern.ch:/afs/cern.ch/user/r/rprivara/private/fluka/* .
	tar xf fluka2025.1-data*
	tar xf fluka2025.1-linux*
	make -j$THR
	cd $WDIR
else
	echo "Fluka binary already exists"
fi

# Clone corsika-sim
if [ ! -d $WDIR/corsika-sim ]; then
	git clone https://github.com/Bembeg/corsika-sim.git
else
	echo "Corsika-sim already cloned"
fi

# Clone corsika
if [ ! -d corsika ]; then
	BRANCH="radek_atmo_models"
	# git clone --recursive https://gitlab.iap.kit.edu/AirShowerPhysics/corsika.git -b $BRANCH
	git clone --recursive git@gitlab.iap.kit.edu:AirShowerPhysics/corsika.git -b $BRANCH

else
	echo "Corsika already cloned"
fi

# Determine whether tests are to be run
if [ "$1" == "1" ] || [ -z "$1" ]; then
	RUN_TESTS=1
else
	RUN_TESTS=0
fi

# Build corsika
cd $WDIR/corsika
mkdir -p build/debug build/release

# Release build
cd $WDIR/corsika/build/release
$WDIR/corsika/conan-install.sh --source-directory $WDIR/corsika --release
$WDIR/corsika/corsika-cmake.sh -c "-DCMAKE_BUILD_TYPE="Release" -DWITH_FLUKA=ON -DCMAKE_INSTALL_PREFIX=$WDIR/corsika/install/release"
make install -j$THR
if [ $RUN_TESTS -eq 1 ]; then
	ctest -j$THR -E "testQGSJetIII|testProposal"
	TEST_REL=$?
fi
cd $WDIR/corsika

# Debug build
cd $WDIR/corsika/build/debug
$WDIR/corsika/conan-install.sh --source-directory $WDIR/corsika --debug
$WDIR/corsika/corsika-cmake.sh -c "-DCMAKE_BUILD_TYPE="Debug" -DWITH_FLUKA=ON -DCMAKE_INSTALL_PREFIX=$WDIR/corsika/install/debug"
make install -j$THR
if [ $RUN_TESTS -eq 1 ]; then
	ctest -j$THR -E "testQGSJetIII|testProposal"
	TEST_DBG=$?
fi
cd $WDIR/corsika

# Test results
if [ $RUN_TESTS -eq 1 ]; then
	echo "Test release build: exit code $TEST_REL"
	echo "Test debug build: exit code $TEST_DBG"
fi

echo "Finished"



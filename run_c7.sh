# Script to run CORSIKA7 simulation

print_help() {
    echo "Usage:"
    echo "$0 [name] [showers] [prim] [energy] [azimuth] [zenith] [obs. level] [cherWavelenMin] [cherWavelenMax] [bunching]" 
}

if [ -z "$1" ]; then
    print_help
    exit 0
fi


# ----------------- CONFIG -----------------
# CORSIKA7 image version
C7_IMAGE="ghcr.io/gammasim/corsika7:v78010-generic"

# CORSIKA7 directory and config file path
C7_DIR=$(realpath "../cta/corsika7-minimal-setup")
C7_CONF_FILE_BASE="${C7_DIR}/conf.input"

# output name
OUT_NAME="$1"

# run and event id
RUN_ID=0
EVT_ID=0
# number of showers
N_SHW=$2

# primary particle type (gamma=1, proton=?)
PRIM=$3
# its energy in GeV
ENE=$4
# azimuth and zenith angles in degrees
AZI=$5
ZEN=$6

# observation level in cm
OBS_LEVEL=$7

# cherenkov wavelength range
CHER_WL_MIN=$8
CHER_WL_MAX=$9
# cherenkov photon bunching
BUNCHING=${10}
# ------------------------------------------

# store this directory
CURRENT_DIR=$(pwd)

# output directory for this run
OUT_DIR=$(realpath "output/${OUT_NAME}")
mkdir -p ${OUT_DIR}

# print config
echo -e "\nCORSIKA7 simulation config:"
echo "  name             : ${OUT_NAME}"
echo "  showers          : ${N_SHW}"
echo "  primary          : ${PRIM}"
echo "  energy [GeV]     : ${ENE}"
echo "  azimuth [deg]    : ${AZI}"
echo "  zenith [deg]     : ${ZEN}"
echo "  obs. level [cm]  : ${OBS_LEVEL}"
echo "  cher. range [nm] : ${CHER_WL_MIN} - ${CHER_WL_MAX}"
echo "  bunching         : ${BUNCHING}"
echo "  output directory : ${OUT_DIR}"

RUN_LOG="${OUT_DIR}/run.log"
RUN_OUTPUT="${OUT_DIR}/output.corsika"
RUN_CONF="${OUT_DIR}/conf.input"

# create a new config file with the requested parameters
cp ${C7_CONF_FILE_BASE} ${RUN_CONF}
sed -i "s|RUNNR.*|RUNNR ${RUN_ID}|" ${RUN_CONF}
sed -i "s|EVTNR.*|EVTNR ${EVT_ID}|" ${RUN_CONF}
sed -i "s|NSHOW.*|NSHOW ${N_SHW}|" ${RUN_CONF}
sed -i "s|PRMPAR.*|PRMPAR ${PRIM}|" ${RUN_CONF}
sed -i "s|ERANGE.*|ERANGE ${ENE} ${ENE}|" ${RUN_CONF}
sed -i "s|THETAP.*|THETAP ${ZEN} ${ZEN}|" ${RUN_CONF}
sed -i "s|PHIP.*|PHIP ${AZI} ${AZI}|" ${RUN_CONF}
sed -i "s|OBSLEV.*|OBSLEV ${OBS_LEVEL}|" ${RUN_CONF}
sed -i "s|CERSIZ.*|CERSIZ ${BUNCHING}|" ${RUN_CONF}
sed -i "s|CWAVLG.*|CWAVLG ${CHER_WL_MIN} ${CHER_WL_MAX}|" ${RUN_CONF}

# copy the config file to the C7 directory 
cp ${RUN_CONF} ${C7_DIR}/conf.input

# check CORSIKA7 image
if [ -z "$(docker image ls | grep ${C7_IMAGE})" ]; then
    echo "C7 image '${C7_IMAGE}' does not exist, please pull it manually"
    exit 1
fi

# enter the C7 directory
cd ${C7_DIR}

# start a C7 container
C7_CONT=$(docker run --rm -itd -v "${C7_DIR}/:/workdir/external" ${C7_IMAGE})
echo "C7 container '${C7_CONT}' started"

# run the C7 simulation
echo -n "Running C7 simulation ... "
docker exec ${C7_CONT} /bin/bash -c './corsika_epos_urqmd_flat < /workdir/external/conf.input' &> ${RUN_LOG}
if [ $? -eq 0 ]; then
    echo "OK"
else
    echo "problem"
fi

# move the output file out of the container
docker exec ${C7_CONT} /bin/bash -c 'mv output.corsika /workdir/external'

# move output file to the output directory
mv -f ${C7_DIR}/output.corsika ${RUN_OUTPUT}

# stop the C7 container 
echo "Stopping C7 container"
docker stop ${C7_CONT} > /dev/null

# check the container stopped
if [ ! -z "$(docker ps | grep ${C7_CONT})" ]; then
    echo "Container '${C7_CONT}' still running"  
fi

# go back to this directory
cd ${CURRENT_DIR}

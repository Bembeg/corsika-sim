#!/bin/bash
# Script for setting up local CTA model database

# Pull simtools image
SIMTOOLS_REL="simtools-sim-telarray-250903-corsika-78010-bernlohr-1.70-prod6-baseline-qgs3-no_opt"
echo -e "\e[34;1mPulling simtools image\e[0m"
docker pull ghcr.io/gammasim/${SIMTOOLS_REL}

# Pull mongoDB image
echo -e "\e[34;1mPulling mongoDB image\e[0m"
docker pull mongo

# Clone CTA simulation models repo
if [ -d "simulation-models" ]; then
    # Only pull changes if repo already cloned
    echo -e "\e[34;1mCTA simulation models exists, pulling changes\e[0m"
    git -C simulation-models pull
else
    echo -e "\e[34;1mCloning CTA simulation models repository\e[0m"
    git clone https://gitlab.cta-observatory.org/cta-science/simulations/simulation-model/simulation-models.git
fi

# Prepare .env file 
ENV_FILE=".env"
if [ -f ${ENV_FILE} ]; then
    echo -e "\e[34;1mEnv-file '${ENV_FILE}' already exists, skipping\e[0m"
else
    echo -e "\e[34;1mGenerating env-file '${ENV_FILE}'\e[0m"
    touch ${ENV_FILE}
    echo "SIMTOOLS_DB_SERVER='simtools-mongodb'" >> ${ENV_FILE}
    echo "SIMTOOLS_DB_API_PORT=27017" >> ${ENV_FILE}
    echo "SIMTOOLS_DB_API_USER='root'" >> ${ENV_FILE}
    echo "SIMTOOLS_DB_API_PW='example'" >> ${ENV_FILE}
    echo "SIMTOOLS_DB_API_AUTHENTICATION_DATABASE='admin'" >> ${ENV_FILE}
    echo "SIMTOOLS_DB_SIMULATION_MODEL='mongo-data'" >> ${ENV_FILE}
    echo "SIMTOOLS_SIMTEL_PATH='/workdir/sim_telarray'" >> ${ENV_FILE}
    echo "SIMTOOLS_USER_NAME='User Name'" >> ${ENV_FILE}
    echo "SIMTOOLS_USER_ORCID='0000-0000-0000-0000'" >> ${ENV_FILE}
fi

# Download setup script from simtools repository
curl -sL https://raw.githubusercontent.com/gammasim/simtools/main/database_scripts/setup_local_db.sh -o db_container.sh

# Check if local model database is set up
if [ -d mongo-data ] && [ $(docker network ls | grep "simtools-mongo-network" | wc -l) -eq 1 ]; then
    echo -e "\e[34;1mLocal model database seems to be set up, skipping creation\e[0m"
else
    echo -n -e "\e[34;1mSetting up local model database ... \e[0m"
    # Remove any leftover containers to start clean
    docker stop simtools-mongodb &> /dev/null
    docker network rm "simtools-mongo-network" &> /dev/null
    docker container rm simtools-mongodb &> /dev/null
    # Remove data directory
    rm -rf mongo-data
    
    # Run setup script
    bash db_container.sh &> /dev/null

    # Check if setup script succeeded or failed
    if [ $? -eq 0 ]; then
        echo -e "\e[34;1mOK\e[0m"
    else
        echo -e "\e[31;1mError\e[0m"
        exit 1
    fi
fi

# Start the mongoDB container if not running already
echo -en "\e[34;1mDatabase container ... \e[0m"
if [ $(docker container ls | grep "simtools-mongodb" | wc -l) -eq 1 ]; then
    echo -e "\e[34;1malready running \e[0m"
else
    docker start simtools-mongodb &> /dev/null
    if [ $? -eq 0 ]; then
        echo -e "\e[34;1mstarted\e[0m"
    else 
        echo -e "\e[31;1mproblem starting\e[0m"
        exit 1
    fi
fi

# Load into the mongo and see if it works
MONGOSH_OUTPUT=$(docker exec -it simtools-mongodb mongosh -u root -p example --authenticationDatabase admin --eval "show databases")
if [ $? -eq 0 ]; then
    echo -e "\e[34;1mSuccessful connection to model database\e[0m"
else 
    echo -e "\e[31;1mProblem connecting to model database\e[0m"
    exit 1
fi

MODEL_VER=(6.2.1 7.0.0)

echo -e "\e[34;1mChecking database content for model versions: ${MODEL_VER[@]}\e[0m"

for VER in ${MODEL_VER[@]}; do
    echo -ne "\e[34;1m  - checking $VER ... "
    VER_DASH=$(echo $VER | tr . -)    
    
    echo "${MONGOSH_OUTPUT}" | grep -q "mongo-data-${VER_DASH}"
    if [ $? -eq 0 ]; then
        echo -e "found in database, skipping\e[0m"
    else
        echo -e "not found in database, pulling\e[0m"

        docker run --platform linux/amd64 --rm -it --network simtools-mongo-network \
            --env-file ${ENV_FILE} -v "$(pwd):/workdir/external" \
            ghcr.io/gammasim/${SIMTOOLS_REL} \
            bash -c "source /workdir/env/bin/activate && simtools-db-add-simulation-model-from-repository-to-db \
            --input_path /workdir/external/simulation-models/simulation-models/model_parameters \
            --db_simulation_model mongo-data \
            --db_simulation_model_version $VER \
            --type model_parameters"
        
        docker run --platform linux/amd64 --rm -it --network simtools-mongo-network \
            --env-file ${ENV_FILE} -v "$(pwd):/workdir/external" \
            ghcr.io/gammasim/${SIMTOOLS_REL} \
            bash -c "source /workdir/env/bin/activate && simtools-db-add-simulation-model-from-repository-to-db \
            --input_path /workdir/external/simulation-models/simulation-models/productions \
            --db_simulation_model mongo-data \
            --db_simulation_model_version $VER \
            --type production_tables"
    fi
done

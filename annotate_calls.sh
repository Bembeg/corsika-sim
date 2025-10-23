#!/bin/bash
# Run callgrind annotate for simulation outputs and process the results

# Directory with simulation outputs
OUTPUT_DIR=${PWD}/output

# Number of highest functions to annotate
FUNCS=10

for SIM in $(ls ${OUTPUT_DIR}); do
    if [ ! -d ${OUTPUT_DIR}/$SIM ]; then continue; fi

    echo "Processing $SIM"

    rm -f ${OUTPUT_DIR}/$SIM/annotate.txt

    for RUN in $(ls ${OUTPUT_DIR}/$SIM); do
        # echo "  Run $RUN"

        DIR=${OUTPUT_DIR}/$SIM/$RUN

        if [ -f $DIR/run.prof ]; then
            # Get annotate content
            CONT="$(callgrind_annotate $DIR/run.prof)"

            # Get program totals
            echo -e "$CONT" | grep "PROGRAM TOTALS" > $DIR/annotate.txt
            
            # Parse top $FUNCS functions
            echo "===" >> $DIR/annotate.txt
            echo -e "$CONT" | head -n $((FUNCS+25)) | tail -n $FUNCS >> $DIR/annotate.txt 

            # Merge all run annotations to one file
            echo "=== $RUN ===" >> ${OUTPUT_DIR}/$SIM/annotate.txt
            echo "$(<$DIR/annotate.txt)" >> ${OUTPUT_DIR}/$SIM/annotate.txt
            echo -e "\n">> ${OUTPUT_DIR}/$SIM/annotate.txt
        fi
    done
done

exit 0

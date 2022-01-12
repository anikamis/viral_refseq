#!/bin/bash

echo "Please enter the version numbers you would like to create:"
read -a versions

echo "Please enter filename containing all species you would like to analyze:"
read filename

lines=$( cat ${filename} )

mkdir readsims

for line in ${lines}
do
    mkdir readsims/${line}_reads

    temp=\|${line}\|

    grep -A1 -m1 ${temp} linearized.fna > readsims/${line}_reads/${line}_full.fna

    echo "grep complete"

    # if grep failed, continue
    if [ ! -s readsims/${line}_reads/${line}_full.fna ]; then
        rm -r readsims/${line}_reads
        continue
    fi

    # simulate reads
    art_bin_MountRainier/art_illumina -ss HS25 -i readsims/${line}_reads/${line}_full.fna -na -l 150 -f 0.5 -o readsims/${line}_reads/${line}_sims

    echo "read simulation complete"

    # running kraken for each species
    for ver in ${versions[@]}
    do
        name=readsims/${line}_reads/${line}_${ver}.txt
        db=databases/viral_build_${ver}/db_${ver}
        
        ./scripts_kraken2/kraken2 --db ${db} readsims/${line}_reads/${line}_sims.fq --report ${name}
    
        echo "version ${ver} complete"
    done
done

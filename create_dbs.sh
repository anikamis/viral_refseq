#!/bin/bash

echo "Please enter the version numbers you would like to create:"
read -a versions

echo "Versions requested:"
for VER in ${versions[@]}
do
    if [ ${VER} -le 0 ] || [ ${VER} -ge 211 ]
    then
        echo "Invalid version number requested: ${VER}"
        exit 1
    fi
    echo "${VER} "
done

#./scripts_kraken2/kraken2-build --download-taxonomy --db .

mkdir databases
cd databases

for VER in ${versions[@]}
do
    mkdir viral_build_${VER}
    mkdir viral_build_${VER}/db_${VER}

    echo "Copying taxonomy..."
    cp -r ../taxonomy viral_build_${VER}/db_${VER}

    echo "Downloading catalog for version ${VER}..."
    if [[ ${VER} -eq 210 ]] 
    then 
       wget "https://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/RefSeq-release210.catalog.gz" -P viral_build_${VER}
    else
        wget "https://ftp.ncbi.nlm.nih.gov/refseq/release/release-catalog/archive/RefSeq-release${VER}.catalog.gz" -P viral_build_${VER}
    fi
    
    CATALOG=viral_build_${VER}/RefSeq-release${VER}.catalog

    echo "Unzipping catalog for version ${VER}..."
    gzip -d ${CATALOG}.gz

    echo "Splicing catalog for version ${VER}..."
    sed -i '/virus\|viral/!d' ${CATALOG}

    cp ${CATALOG} viral_build_${VER}/temp.catalog
    gzip ${CATALOG}

    # creating countVER.txt files
    echo "Counting species for version ${VER}..."
    myarr=( $( awk -F '\t' '{ print $1 }' viral_build_${VER}/temp.catalog | sort -u) )
    countfile=viral_build_${VER}/count${VER}.txt

    for spe in ${myarr[@]}
    do
        count=( $(grep ${spe} viral_build_${VER}/temp.catalog | wc -l ) )
        line=${spe}$'\t'${count}

        echo ${line} >> ${countfile}
    done
    
    echo "Running refseq_rollback.pl for version ${VER}..."
    ../refseq_rollback/scripts/refseq_rollback.pl -fasta ../viral_refseq_cat.fna -catalog ${CATALOG}.gz -out viral_build_${VER}/release${VER}.fasta
    
    echo "Adding file to library for version ${VER}..."
    ../scripts_kraken2/kraken2-build --add-to-library viral_build_${VER}/release${VER}.fasta --db viral_build_${VER}/db_${VER}

    echo "Building database for version ${VER}..."
    ../scripts_kraken2/kraken2-build --build --db viral_build_${VER}/db_${VER}

    echo "Success for version ${VER}!"
done

cd ..

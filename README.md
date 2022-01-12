# viral_refseq

Dependencies:

Within the same directory as all the source files in this repository, you must also have:
  1. a directory named "scripts_kraken2" that contains all the scripts from Kraken2
  a. refer to github.com/DerrickWood/kraken2/ for download instructions, scripts are located within github.com/DerrickWood/kraken2/tree/master/scripts
  
  2. a directory named "art_bin_MountRainier" containing the binaries for the ART illumina simulator
  a. refer to https://www.niehs.nih.gov/research/resources/software/biostatistics/art/index.cfm
  
  3. a directory named "refseq_rollback" containing the scripts used by the Nasko paper
  a. refer to https://github.com/dnasko/refseq_rollback
  
  4. a file named "species.txt" containing a list of taxonomic ids of species which the user desires to analyze


I ran the python program in an Anaconda virtual environment, for which the reqs.yml file had all the necessary packages installed for the python file.

For the two bash scripts, run "chmod u+x <file.sh>" to be able to run them as executables.

This repo contains:
1. linearized.fna: a FASTA file containing all the viral species present in refseq as well as its full genome sequence linearized

3. create_dbs.sh: a bash script that will create Kraken2 databases for the desired versions
a. this calls scripts from scripts_kraken2 & refseq_rollback

4. sim_and_kraken.sh: a bash script that will create simulated reads all the species in "species.txt", and then run Kraken2 on the reads using the database for each version
a. this calls scripts from scripts_kraken2 and art_bin_MountRainier

6. tree_parse.py: a python script that will create "final.csv", which summarizes all the nodes and their sizes over versions, and "kraken.csv", which summarizes the kraken2 output of the desired species from the file. Please note that as of now, this script has hardcoded version numbers 70, 80, 90, 200, 208.

In order to yield the same data, run the three scripts in listed order above (./create_dbs.sh, ./sim_and_kraken.sh, tree_parse.py)

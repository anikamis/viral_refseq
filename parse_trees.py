
#!/usr/bin/env python3
""" Parse the NCBI taxonomy """

import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt

from typing import Dict, List, Tuple

#ranks we care about
ranks = ["strain", "species", "genus", "family", "order", "class", "phylum", "kingdom", "no rank"]

class Node:
	""" Definition of the class Node """
	def __init__(self):
		self.tax_id = "0"     # Number of the tax id.
		self.parent = "0"     # Number of the parent of this node
		self.children = []    # List of the children of this node
		self.division = None  # Division.
		self.is_tip = True    # Tip = True if it's a terminal node, False if not.
		self.name = ""        # Name of the node: taxa if it's a terminal node, number if not.
		self.val = 1          # Number of leaves in descendants
		self.anc = []         # All ancestors with ranks we care about


def get_genealogy(name_object, leaf_node: str) -> List[str]:
	""" Trace genealogy from root to leaf """
	ancestors = []  # Initialise the list of all nodes from root to leaf.
	gen_tax_id = leaf_node  # Define leaf
	while 1:
		if gen_tax_id in name_object:
		    ancestors.append(gen_tax_id)
		    gen_tax_id = name_object[gen_tax_id].parent  # Move up to parents
		else:
		    break
		if gen_tax_id == "1":
		    # If it is the root, we reached the end.
		    # Add it to the list and break the loop
		    ancestors.append(gen_tax_id)
		    break
	return ancestors  # Return the list


def _get_all_descendant_nodes(name_object, taxid: str) -> List[str]:
    """ Get all descendant of a node recursively """
    descendant_nodes: List[str] = [taxid]
    if len(name_object[taxid].children) > 0:
        for child in name_object[taxid].children:
            descendant_nodes = descendant_nodes + _get_all_descendant_nodes(name_object, child)
    return descendant_nodes


def _get_iterative(ncbi, taxid: str) -> List[str]:
    """ Get all descendant of a node iteratively """
    total : List[str] = [taxid]
    to_visit : List[str] = [taxid]
    
    while len(to_visit) != 0:
        curr = to_visit.pop(0)
        
        to_visit += ncbi[curr].children
        total += ncbi[curr].children
    
    return list(set(total))


def _keep_terminal(name_object, nodes_list) -> List[str]:
    """ Keep only terminal nodes """
    terminal_nodes = []
    
    for x in nodes_list:
        if name_object[x].is_tip:
            name_object[x].val = 1
            terminal_nodes.append(x)
    
    return terminal_nodes


def _keep_terminal_parents(name_object, nodes_list) -> List[str]:
    """ Keep only immediate parents of terminal nodes """
    nodes = {name_object[x].parent for x in nodes_list if name_object[x].is_tip}
    
    return nodes


def _keep_division(name_object, nodes_list, target_division) -> List[str]:
    """ Keep only division nodes """
    division_nodes = [x for x in nodes_list if name_object[x].division == target_division]
    return division_nodes


def get_all_descendants(name_object, target_division: str, taxid: str) -> List[str]:
    """ Get all taxa of a node """
    terminal_nodes = _get_all_descendant_nodes(name_object, taxid)
    terminal_nodes = _keep_division(name_object, terminal_nodes, target_division)

    return terminal_nodes  # Return a list


def get_common_ancestor(name_object, node_list: List[str]):
    """
    Function to find common ancestor between two nodes or more
    Args:
        name_object (name_object): taxonomy to use
        node_list (list): list of node
    Returns:
        node (str): node of the common ancestor between nodes
    """

    # global name_object
    list1 = get_genealogy(name_object, node_list[0])  # Define the whole genealogy of the first node
    ancestral_list: List[str] = []
    for node in node_list:
        list2 = get_genealogy(name_object, node)  # Define the whole genealogy of the second node
        ancestral_list = []
        for taxid in list1:
            if taxid in list2:  # Identify common nodes between the two genealogy
                ancestral_list.append(taxid)
        list1 = ancestral_list  # Reassigning ancestral_list to list 1.
    last_common_ancestor = ancestral_list[
        0
    ]  # Finally, the first node of the ancestral_list is the common ancestor of all nodes.
    return last_common_ancestor  # Return a node


def load_ncbi_names(filename: str = "names.dmp") -> Tuple[Dict, Dict]:
    """Load NCBI names definition ("names.dmp")
    Args:
        filename (str): filename of NCBI names
    Returns:
        name_dict, name_dict_reverse
    """

    name_dict = {}  # Initialise dictionary with TAX_ID:NAME
    name_dict_reverse = {}  # Initialise dictionary with NAME:TAX_ID

    name_file = open(filename, "r")
    while 1:
        line = name_file.readline()
        if line == "":
            break
        line = line.rstrip()
        line = line.replace("\t", "")
        tab = line.split("|")
        if tab[3] == "scientific name":
            tax_id, name = tab[0], tab[1]  # Assign tax_id and name ...
            name_dict[tax_id] = name  # ... and load them
            name_dict_reverse[name] = str(tax_id)  # ... into dictionaries
    
    name_file.close()
    return name_dict, name_dict_reverse


def load_ncbi_taxonomy(name_dict, filename: str = "nodes.dmp"):
    """Load taxonomy NCBI file ("nodes.dmp")
    Args:
        filename (str): filename of ncbi taxonomy
        name_dict (dict): name_dict
    Returns:
    """

    # Define taxonomy variable
    # global name_object
    name_object: Dict = {}

    taxonomy_file = open(filename, "r")
	
    lines = taxonomy_file.readlines()
    for line in reversed(lines):
        line = line.replace("\t", "")
        tab = line.split("|")

        tax_id = str(tab[0])
        tax_id_parent = str(tab[1])
        division = str(tab[2]).lower()

        # Define name of the taxonomy id
        name = "unknown"
        if tax_id in name_dict:
            name = name_dict[tax_id]

        if tax_id not in name_object:
            name_object[tax_id] = Node()

        name_object[tax_id].tax_id = tax_id  # Assign tax_id
        name_object[tax_id].parent = tax_id_parent  # Assign tax_id parent
        name_object[tax_id].name = name  # Assign name
        name_object[tax_id].division = division  # Assign name
		

        # Add it has children to parents
        children_list = []
        if tax_id_parent in name_object:
            children_list = name_object[tax_id_parent].children  # If parent is in the name_object
            
        else:
            name_object[tax_id_parent] = Node()
            name_object[tax_id_parent].tax_id = tax_id_parent  # Assign tax_id


        children_list.append(tax_id)  # ... we found its children.
        name_object[tax_id_parent].children = children_list  # ... so add them to the parent

        # As the parent node is found, it is not a terminal node then
        name_object[tax_id_parent].is_tip = False

    taxonomy_file.close()

    return name_object


def count_genomes(ncbi, filename):
    """Load file containing species and number of terminal nodes ('count.txt')

    Used when examining number of genomes a species has
    When val = number of genomes a node has in its descendants

    """

    # Define taxonomy variable
    # global name_object
    cat: Dict = {}

    cat_file = open(filename, "r")
	
    lines = cat_file.readlines()
    
    for line in lines:
        if line == "":
            break

        tab = line.split()

        tax = str(tab[0])
        count = int(tab[1])
        
        if tax not in ncbi:
            continue
        
        ancestry = get_genealogy(ncbi, tax)
        
        curr = Node()
        if tax in cat:
            curr = cat[tax]
        else:
            curr = ncbi[tax]
            
        for an in ancestry:
            if an not in ncbi:
                continue
                
            if an not in cat:
                cat[an] = ncbi[an]
            
            cat[an].val += count

    cat_file.close()

    return cat

def analyze_kraken(ncbi, finaldf, filename):
	names = open(filename, "r")
	read_names = names.readlines()

	cols = ["size", "reads", "species", "genus", "higher", "version"]

	indices = []
	rows = []

	for line in read_names:
		line = str(line).strip()

		if line not in finaldf.index or line not in ncbi:
			continue

		sizes = findf.loc[line].to_list()
		versions = ["70", "80", "90", "200", "280"]

		size = 1
		ancestors = [z for z in ncbi[line].anc]

		while size < 6:
			curr_row = [str(sizes[size]), "0", "0", "0", "0", versions[size - 1]]

			fname = "readsims/" + line + "_reads/" + line + "_" + versions[size - 1] + ".txt"

			try:
				kraken = open(fname, "r")
			except FileNotFoundError:
				break
			
			rev = kraken.readlines()
			reads = [0, 0, 0]

			for r in rev:
				r = r.replace("\n", "")
				sp = r.split('\t')

				krakid = str(sp[4])

				if krakid == "1":
					curr_row[1] = str(sp[1])
					reads[2] = str(sp[1])
				
				if krakid in ancestors:
					# if found correct genus
					if str(sp[3].lstrip() == "G"):
						reads[1] = str(sp[2]).lstrip() # number reads assigned directly to genus
					# if found correct species
					elif str(sp[3].lstrip() == "S"):
						reads[0] = str(sp[1]).lstrip() # number reads rooted at species
			
			# number reads classified higher than genus is total - genus - species
			reads[2] = int(reads[2]) - int(reads[1]) - int(reads[0])

			# add to row
			curr_row[2] = str(reads[0])
			curr_row[3] = str(reads[1])
			curr_row[4] = str(reads[2])

			indices.append(line)
			rows.append(curr_row)

			size += 1
	
	return pd.DataFrame(rows, columns = cols, index = indices)

def prune_ranks(ncbi, names):
    """ Traverses tree and calculates value of each node

    Used when examining number terminal classification nodes a node has
    When val = number of descendant nodes

    """

    term = _keep_terminal(ncbi, names.keys())
    
    for t in term:
        ancestors = get_genealogy(ncbi, t)
        
        for a in ancestors:
            ncbi[a].val += 1
            
    return ncbi


# non-recursive method to get value if examining number of descendants
def get_val(ncbi, tax, terminal):
    
    if ncbi[tax].val == 0:
        term = set(terminal)
        desc = set(_get_iterative(ncbi, tax))
        
        # size of intersection
        num = len(term & desc)
        ncbi[tax].val = num
        
    return ncbi[tax].val      


# outputs data for examining number of descendants
def family_size(ncbi, name):
    term = _keep_terminal(ncbi, name.keys())
    
    cols = ["rank", "1", "2", "3", "4", "5", "6", "7", "8"]
    all_rows = []
    indices = []
    
    # iterate over terminal nodes
    for tax in term:
        if (tax == "1" or tax in indices): #if root or already calculated
            continue
        
        curr = ncbi[tax]

       # if curr is not in a valid rank,
       # iterate through ancestors until we find one with valid rank 
        while ((not (curr.division in ranks)) or (curr.division == "no rank" and curr.tax_id != "1")):
            curr = ncbi[curr.parent]
        

        # if curr is already accounted for, or its an invalid rank
        if curr.tax_id in indices or curr_division == "no rank" or (not curr.division in ranks):
            continue
 

        all_ancestors = get_genealogy(ncbi, curr.tax_id)
        
        # contains all ancestors with valid ranks
        ranked = []

        #list comprehension method
        ranked = [z for z in all_ancestors if ncbi[z].division in ranks and not (ncbi[z].division == "no rank" and ncbi[z].tax_id != "1")]

        # crude method
        #for z in all_ancestors:
        #    if (ncbi[z].division == "no rank" and z != "1"):
        #        continue
        #        
        #    elif ncbi[z].division in ranks:
        #        ranked.append(z)

        
        values = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        values[0] = ranks.index(curr.division)

        i = 1

        # add curr to df
        while i < len(ranked):
            values[i] = ncbi[ranked[i]].val - ncbi[ranked[i - 1]].val     
            i += 1
            
        all_rows.append(values)
        indices.append(curr.tax_id)
        
        k = 1
        y = 8
        
        while values[y - 1] == "0":
            y -= 1

        # add curr's ancestors each to df as well
        while (k < len(ranked) and ranked[k] != "1"):
            curr_tax = ranked[k]
            
            if ncbi[curr_tax].tax_id in indices:
                break
                
            temp = values[k+1:]
            temp.insert(0, ranks.index(ncbi[curr_tax].division))
            
            while (len(temp) < len(values)):
                temp.insert(len(temp) - 1, "0")
                
            indices.append(curr_tax)
            all_rows.append(temp)
            
            k += 1

    return pd.DataFrame(all_rows, columns = cols, index = indices)


def genome_size(ncbi):
    cols = ["rank", "genomes"]
    all_rows = []
    indices = []

    for tax in ncbi.keys():
        curr = ncbi[tax]
        if tax not in indices and curr.division != "no rank" and curr.division in ranks:
            indices.append(tax)
            all_rows.append([ranks.index(curr.division), curr.val])
            ncbi[tax].anc = [z for z in get_genealogy(ncbi, tax) if (ncbi[z].division in ranks and ncbi[z].division != "no rank") or z == "1"]

    return pd.DataFrame(all_rows, columns = cols, index = indices)

# Load name_dict, name_dict_reverse and taxonomy
name_dict, name_dict_reverse = load_ncbi_names(filename="taxonomy/names.dmp")  # Load names
print("names loaded...")


ncbi_taxonomy = load_ncbi_taxonomy(filename="taxonomy/nodes.dmp", name_dict=name_dict)
print("taxonomy loaded...")

# do below if examining number of descendant terminal classification nodes a node has
#ncbi_taxonomy = prune_ranks(ncbi_taxonomy, name_dict)
#final_df = family_size(ncbi_taxonomy, name_dict)

versions = ["70", "80", "90", "200", "208"]

indices=[]
all_rows=[]
cols = ["rank", "70", "80", "90", "200", "208"]

dfs = []
df70 = pd.DataFrame()
counted = dict()

# count genomes for each database version
for v in versions:	
	counted = dict()
	
	counted = count_genomes(ncbi_taxonomy, filename="databases/viral_build_" + v + "/count" + v + ".txt")

	print("counted genomes for version " + v)

	if (v == "70"):
		df70 = genome_size(counted)
	else:
		dfs.append(genome_size(counted))
	
	ncbi_taxonomy = load_ncbi_taxonomy(filename="taxonomy/nodes.dmp", name_dict=name_dict)
	print("genomes sized for version  " + v)

# iterate over all databases to get final.csv
for ind in df70.index:
	values=df70.loc[ind].to_list()
    
	for df in dfs:
		if ind in df.index:
			values.append(df.loc[ind].to_list()[1])
    
		if len(values) == 6:
			indices.append(ind)
			all_rows.append(values)
        
findf = pd.DataFrame(all_rows, columns = cols, index = indices)
findf.to_csv("final.csv")

print("counts concatenated...")

analyze_kraken(counted, findf, "species.txt").to_csv("kraken.csv")

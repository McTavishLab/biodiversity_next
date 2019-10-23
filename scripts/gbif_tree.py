import sys
from physcraper import opentree_helpers
from physcraper.treetaxon import TreeTax

#read in GBIF download, e.g. 
filename = sys.argv[1]
fi = open(filename)
header = fi.readline().split('\t')

sys.stdout.write("Getting OpenTree synthetic tree for taxa in {}\n".format(filename))

#Get indexes for each column in the csv file
col_dict = {}
for i, col in enumerate(header):
    col_dict[col] = i


sys.stdout.write("Matching ids\n")

match_dict = {}
gbif_ids = []
ott_ids = []
i = 0
#Looop trhough each line in the file
for lin in fi:
    i += 1
    sys.stdout.write(".") #progress bar
    sys.stdout.flush()
    lii = lin.split('\t')
    gb_id = lii[col_dict['taxonKey']]
    if gb_id in match_dict:
        #Skip gb_id's you have already matched
        pass
    else:
        # Do a driect match to gbif id's in the open tree taxnomy
        ott_id = opentree_helpers.get_ottid_from_gbifid(gb_id)
        match_dict[gb_id] = ott_id
        if ott_id == None:
            # If GBIF id isn' found in the open tree taxonomy, search on scientific name
            spp_name = lii[col_dict['verbatimScientificName']]
            ott_id, ott_name, ncbi_id = opentree_helpers.get_ott_taxon_info(spp_name)
            if ott_id:
                match_dict[gb_id] = ott_id
                ott_ids.append(ott_id)
            else:
                # Some names still won't match
                ott_id = None
        ott_ids.append(ott_id)


ott_ids = set(ott_ids)
if None in ott_ids:
    ott_ids.remove(None)

trefile = "names.tre"
#Get the syntehtic tree from OpenTreem and withe the ciattions to a text file.
tre = opentree_helpers.get_tree_from_synth(list(ott_ids), label_format = "name", citation="cites.txt")
tre.write(path = "names.tre", schema = "newick")


sys.stdout.write("Tree written to {}\n".format(trefile))

import sys
from opentree import OT




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
        gbiftax = "gbif:{}".format(int(gb_id))
        res = OT.taxon_info(source_id=gbiftax)
        if res.status_code == 200:
            ott_id = int(res.response_dict['ott_id'])
            match_dict[gb_id] = ott_id
        if res.status_code == 400:
            # If GBIF id isn' found in the open tree taxonomy, search on scientific name
            spp_name = lii[col_dict['verbatimScientificName']]
            sys.stdout.write("{},{} not matched on ID\n".format(gbiftax, spp_name))
            res2 = OT.tnrs_match([spp_name])
            if res2.status_code == 200:
                if len(res2.response_dict['results']) > 0:
                    ott_id = int(res2.response_dict['results'][0]['matches'][0]['taxon']['ott_id'])
                    match_dict[gb_id] = ott_id
                    ott_ids.append(ott_id)
                    sys.stdout.write("{},{} matched on name to ott id{}\n".format(gbiftax, spp_name, ott_id))
                else:
                    sys.stdout.write("{},{} still NO MATCH\n".format(gbiftax, spp_name))
                    match_dict[gb_id] = None
        ott_ids.append(ott_id)


ott_ids = set(ott_ids)
if None in ott_ids:
    ott_ids.remove(None)

trefile = "names.tre"
#Get the syntehtic tree from OpenTreem and withe the ciattions to a text file.
output = OT.synth_induced_tree(ott_ids=list(ott_ids),  label_format='name')
output.tree.write(path = "names.tre", schema = "newick")
sys.stdout.write("Tree written to {}\n".format(trefile))


studies = output.response_dict['supporting_studies']

for study in studies:
    studyid = study.split('@')[0]
    studyres = OT.find_studies(studyid, search_property = 'study_id')
    new_cite = studyres.response_dict.get('matched_studies', None)
    if new_cite:
        f.write(to_string(new_cite[0].get('ot:studyPublicationReference', '')) + '\n' + new_cite[0].get('ot:studyPublication', '') + '\n')



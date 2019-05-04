# COST STSM Wikification 2019.3

The archive of the code created for the STSM titled "Named-entity recognition with wikification using Wikidata in the Hungarian part of the ELTEc corpus"

## Contents

- [hun_POS_5000_e-magyar.csv](hun_POS_5000_e-magyar.csv): An [stratified random sample](https://github.com/ELTE-DH/COST-ELTeC-tools/) of 5000 token from the [Hungarian ELTEc corpus](https://github.com/COST-ELTeC/ELTeC-hun) POS tagged with [e-magyar](http://e-magyar.hu/en)
- [main.py](main.py): A pilot implementation of the wikifier using Bert embeddings to disambiguate by using context
- [query3.sparql](query3.sparql) and [query_wikidata.sh](query_wikidata.sh) are the Sparql and the Query script to gather names and aliases for all living person entry in the wikidata. It yields more customizable results compared to [NECKAr](https://event.ifi.uni-heidelberg.de/?page_id=532) dataset
- [result.csv](result.csv), [result3.csv](result3.csv), [result3_mod.csv](result_mod.csv) are the results of the Sparql query
- [scratch.py](scratch.py): Gather statistics from the results obtained from Wikidata
- [tagged.txt](tagged.txt): The Wikified corpus sample. (No found entries because they are all fictive characters.)
- [wikifier](wikifier): Tool to parse eltec-level0 and annotate words with wikipedia entries. Makes use of http://wikifier.org/

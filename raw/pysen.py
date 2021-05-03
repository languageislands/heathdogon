from csvw.dsv import UnicodeReader
from pysen.glosses import to_concepticon
from lexibank_heathdogon import Dataset

with UnicodeReader(ds().etc_dir.joinpath("concepts.tsv"), delimiter="\t") as reader:
    concepts = [row for row in reader]

mapped = []
for row in concepts:
    gloss = {"gloss": row[1]}
    matches = to_concepticon(gloss)[row[1]]
    if matches:
        concepticon_id, concepticon_gloss, pos, _ = matches[0]
        mapped += [[row[0], row[1], concepticon_id, concepticon_gloss, pos]]
    else:
        mapped += [[row[0], row[1], '', '', '']]

with open(ds().etc_dir.joinpath("concepts-mapped.tsv"), "w") as f:
    f.write("NUMBER\tENGLISH\tCONCEPTICON_ID\tCONCEPTICON_GLOSS\tPOS\n")
    for row in sorted(mapped, key=lambda x: (x[3], x[2]), reverse=True):
        f.write("\t".join(row)+"\n")
print(len([x for x in mapped if x[3]]))
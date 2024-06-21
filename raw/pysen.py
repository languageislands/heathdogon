from csvw.dsv import UnicodeReader
from pysem.glosses import to_concepticon

with UnicodeReader("../etc/concepts.tsv", delimiter="\t") as reader:
    concepts = [row for row in reader]

mapped = []
count = 0
for row in concepts[1:]:
    gloss = {"gloss": row[1]}
    matches = to_concepticon([gloss])[row[1]]
    if matches:
        concepticon_id, concepticon_gloss, pos, _ = matches[0]
        mapped += [row[:7]+[concepticon_id, concepticon_gloss, pos]]
    else:
        matches = to_concepticon([{"gloss": row[2]}], language="fr")[row[2]]
        if matches:
            concepticon_id, concepticon_gloss, pos, _ = matches[0]
            mapped += [row[:7]+[concepticon_id, concepticon_gloss, pos]]
        else:
            mapped += [row[:7] + ['', '', '']]


with open("../etc/concepts-mapped.tsv", "w") as f:
    f.write("NUMBER\tENGLISH\tFRENCH\tENGLISH_SHORT\tFRENCH_SHORT\tENGLISH_CATEGORY\tFRENCH_CATEGORY\tCONCEPTICON_ID\tCONCEPTICON_GLOSS\tPOS\n")
    for row in sorted(mapped, key=lambda x: (x[2], x[1]), reverse=True):
        f.write("\t".join(row)+"\n")
print(len([x for x in mapped if x[-1]])/len(mapped))


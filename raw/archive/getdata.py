from lingpy import *
from clldutils.misc import slug

wl = Wordlist('data.tsv')

with open('../etc/languages.tsv', 'w', encoding='utf8') as f:
    f.write('ID\tName\tGlottocode\tSubGroup\tLatitude\tLongitude\n')
    for l in wl.cols:
        f.write(slug(l, lowercase=False)+'\t'+l+'\t\t\t\t\n')

with open('../etc/concepts.tsv', 'w', encoding='utf8') as f:
    f.write('NUMBER\tENGLISH\tPOS\n')
    cmap = {}
    for idx, concept, pos in wl.iter_rows('concept', 'pos'):
        if concept in cmap:
            pass
        cmap[concept] = pos
    for i, (concept, pos) in enumerate(sorted(cmap.items())):
        f.write(str(i+1)+'\t'+concept+'\t'+pos+'\n')
        


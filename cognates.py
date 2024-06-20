from sys import argv
from lingpy.compare.partial import Partial
from lingpy import Alignments, Wordlist

# load wordlist as Wordlist class
wl = Wordlist(argv[1])

# store original column names to only retain important info
columns = [c for c in wl.columns] + ["cogids"]

# load wordlist as lexstat object (this adds more columns to the data)
lex = Partial(argv[1])

# run analysis
lex.get_partial_scorer(runs=10000)
lex.partial_cluster(ref="cogids", method="lexstat", threshold=0.55, cluster_method="infomap")

# get new wordlist with cognates (without the specific columns)
new_wl = {0: columns}
for idx in lex:
    new_wl[idx] = [lex[idx, c] for c in columns]

# make alignment analysis
alms = Alignments(new_wl, transcription="form", ref="cogids")
alms.align(method="library")

alms.output("tsv", filename=argv[1][:-4] + "-aligned", ignore="all",
            prettify=False)

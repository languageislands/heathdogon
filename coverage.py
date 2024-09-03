from lingpy import *
import collections
from tabulate import tabulate


def get_coverage():
    data="heathdogon-ungrouped.tsv"
    wl = Wordlist(data)

    retain = []
    for language, coverage in wl.coverage().items():
        if coverage > 750:
            retain += [language]

    # create new wordlist
    new_wl = {0: [c for c in wl.columns]}
    for idx, language in wl.iter_rows("doculect"):
        if language in retain:
            new_wl[idx] = wl[idx]
    new_wl = Wordlist(new_wl)

    # select concepts
    concepts = collections.defaultdict(lambda: {k: 0 for k in new_wl.cols})
    for idx, concept, language in new_wl.iter_rows("concept", "doculect"):
        concepts[concept][language] = 1

    # determine if concept is in Swadesh range
    swadesh = {}
    for idx, concept, sw in wl.iter_rows("concept", "swadesh"):
        swadesh[concept] = 1 if sw == "1" else 0

    # restrict to 300 concepts
    sorted_concepts = sorted(concepts, key=lambda x: (swadesh[x],
                                                    sum(concepts[x].values())),
                            reverse=True)[:300]

    # create new wordlist
    new_wl = {0: [c for c in wl.columns]}
    for idx, language, concept in wl.iter_rows("doculect", "concept"):
        if language in retain and concept in sorted_concepts:
            new_wl[idx] = wl[idx]

    new_wl = Wordlist(new_wl)
    new_wl.output('tsv', filename=data[:-4] + "-shortened", prettify=False,
                ignore="all")
    print("New Wordlist has {0} Languages and {1} concepts".format(
        new_wl.width,
        new_wl.height))
    table = []
    for language, coverage in new_wl.coverage().items():
        table += [[language, coverage, coverage / new_wl.height]]
    print(tabulate(table, headers=["language", "items", "coverage"],
                floatfmt=".2f"))

if __name__ == "__main__":
    get_coverage()
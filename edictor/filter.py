from lingpy import *

def run(wordlist):
    D = {0: [c for c in wordlist.columns if c != "swadesh"]}
    for idx in wordlist:
        if wordlist[idx, "swadesh"] == "1":
            D[idx] = [wordlist[idx, c] for c in D[0]]
    return D

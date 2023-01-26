from lingpy import *

def run(wordlist): 
    lex = LexStat(wordlist) 
    lex.cluster( 
        method="sca", 
        threshold=0.45, 
        ref="autocogid") 
    D = {0: wordlist.columns+["autocogid"]} 
    for idx in lex: 
        D[idx] = [lex[idx, h] for h in D[0]] 
    return D
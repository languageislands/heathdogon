from utils import NounParser,VerbParser,AdjectiveNumeralParser
import pandas as pd
import numpy as np
from lingpy import *
from lingpy.sequence.sound_classes import check_tokens
from lingpy.compare.util import (mutual_coverage_check, mutual_coverage_subset)
from lingpy.compare.sanity import average_coverage


#Instantiating parser objects
noun_parser=NounParser()
verb_parser=VerbParser()
adj_num_parser=AdjectiveNumeralParser()


def prior_forms(row):
    """
    puts all forms that have been parsed into a single column
    """
    if pd.isna(row["POS"]):  
        return None
    elif row["POS"] in ["noun", "numeral", "adjective"]:
        form = str(row["SINGULAR"]) if isinstance(row["SINGULAR"], str) else ""
        return form
    elif row["POS"] == "verb":
        verb = row["FORM"]
        if pd.isna(verb):
            return None
        else:
            return verb
    else:
        form = str(row["SINGULAR"]) if isinstance(row["SINGULAR"], str) else ""
        return form




def parsing_data(row):
    """
    puts all forms that have been parsed into a single column
    """
    if pd.isna(row["POS"]):  
        return None
    elif row["POS"]=="noun":
        noun=row["BEFORE_PARSE"]
        if pd.isna(noun):
            return None
        else:
            noun=(noun_parser.identified_suffixes(
            noun_parser.hyphen_space(
                noun_parser.nasalized_stops(
                    noun_parser.cvcv_segmentation(
                            noun_parser.parse_off_final_nasals(
                                noun_parser.existing_parses(
                                    adj_num_parser.y_suffixes(noun.strip("()/_"))))))))) if (noun.endswith("y") or (noun.endswith("ⁿ") and noun[-2]=="y")) else \
                            (noun_parser.identified_suffixes(
                                noun_parser.hyphen_space(
                                    noun_parser.nasalized_stops(
                                        noun_parser.cvcv_segmentation(
                                                noun_parser.parse_off_final_nasals(
                                                    noun_parser.existing_parses(noun.strip("()/_"))))))))
            return noun
            
    elif row["POS"] == "numeral" or row["POS"] == "adjective":
        form = row["BEFORE_PARSE"]
        if pd.isna(form):
            return None
        else:
            form=adj_num_parser.miscellaneous(
            adj_num_parser.switch_hyphen_position(
                adj_num_parser.replace_hyphens_keep_last(
                    adj_num_parser.y_suffixes(
                        adj_num_parser.isolating_suffixes(
                                adj_num_parser.existing_parses(form.strip("()/_")))))))
            return form
    elif row["POS"] == "verb":
        verb = row["BEFORE_PARSE"]
        if pd.isna(verb):
            return None
        else:
            verb=verb_parser.post_editing_short_strings(
            verb_parser.segment_cvcs(
                    verb_parser.existing_parses(verb.strip(")(_"))))
            return verb
    else:
        form = str(row["BEFORE_PARSE"]) if isinstance(row["BEFORE_PARSE"], str) else ""
        return form


def remove_spaces(word):
    if word is None:
        return None
    new_word=""
    for letter in word:
        if letter==" ":
            new_word += ""
        else:
            new_word += letter
    return new_word

def lexstatExperiment(input_file, coverage_num, output_type, output_name):
    """
    Takes an input file and outputs an alignment
    input_file: any_name
    coverage_num: coverage number
    output_type: any_name
    output_name:any_name
    """
    wl = Wordlist(input_file)
    retain = []
    for language, coverage in wl.coverage().items():
        if coverage > coverage_num:
            retain.append(language)
    
    new_wl = {0: [c for c in wl.columns]}
    for idx, language in wl.iter_rows("doculect"):
        if language in retain:
            new_wl[idx] = wl[idx]
    new_wl = Wordlist(new_wl)
    
    #use lexstat model to get cognate clusters
    lex = LexStat(new_wl)
    lex.get_scorer(runs=10000)
    lex.cluster(method='lexstat', threshold=0.55, ref='cogid')

    #get alignments
    alm=Alignments(lex, ref="cogid")
    alm.align()
    return alm.output(output_type,filename=output_name)
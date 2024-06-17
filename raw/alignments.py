from functions import prior_forms,parsing_data,remove_spaces,lexstatExperiment
import pandas as pd
import numpy as np
from segments.tokenizer import Tokenizer
from sys import argv

#loading data
data = pd.read_csv(argv[1], sep="\t", encoding="utf-8")

#dropping unwanted columns
list_to_drop=["ID","FRENCH", "ENGLISH_SHORT", "FRENCH_SHORT", "ENGLISH_CATEGORY", "FRENCH_CATEGORY", "PARSED FORM", "MCF", "RECONSTRUCTION", "NOTE", "NOTES","Unnamed: 18", "Unnamed: 19", "Unnamed: 20", "Unnamed: 21", "COGID", "COGIDS", "Unnamed: 24"]
data=data.drop(list_to_drop, axis=1)

#pulling neccesary data together
data["BEFORE_PARSE"]=data.apply(prior_forms, axis=1) 

#segmenting data
data["PARSED"]=data.apply(parsing_data,axis=1)

#using orthography profile
tk = Tokenizer('orthography.tsv')
data["IPA"]=data["PARSED"].apply(lambda x: tk(x, column="IPA") if isinstance(x, str) else x) 

#cleaning spaces
data["IPA"]=data["IPA"].apply(remove_spaces)
data=data[["DOCULECT", "GLOSS", "IPA"]].dropna(subset=["DOCULECT", "GLOSS", "IPA"])

#drop empty columns and delete 'Mombo', '(1Pl subject pronominal)', 'ǹ' as well, else lingpy throws an error
data.replace("", np.nan, inplace=True)
data = data.dropna(subset=["IPA"])
data = data.drop(data.loc[(data["GLOSS"] == "(1Pl subject pronominal)") & (data["DOCULECT"] == "Mombo")].index)

#output cleaned and formatted data
data.to_csv("notebook_4_1.tsv", index=False, encoding="utf-8", sep='\t')

#load data and conduct alignments
lexstatExperiment("notebook_4_1.tsv", 288, "tsv", "alignments")

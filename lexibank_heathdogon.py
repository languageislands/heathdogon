from pathlib import Path
from clldutils.misc import slug
from pylexibank import FormSpec, Lexeme, Concept, Language
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar
from lingpy import *
import attr

@attr.s
class CustomConcept(Concept):
    PartOfSpeech = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)
    NameInSource = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "heathdogon"
    language_class = CustomLanguage
    concept_class = CustomConcept
    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")", "[": "]"},  # characters that function as brackets
        separators=";/,&~,\\",  # characters that split forms e.g. "a, b".
        missing_data=("∅", "?", "-", "{I", "-:_", "xxx", "-ⁿ"),  # characters that denote missing data.
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=True,  # We ignore all the plural forms
        replacements=[
            ('\u232b', ''),
            (",̀̌[X mà cɛ́nɛ̀] "[1:], ""),
            ("… ", ""),
            ("ADJ ", ""),

            ("\u030c ", ""),
            (" \u030c", ""),
            ("[X cɛ́lɛ̀] ɲàwⁿá", "ɲàwⁿá"),
            ("[X cɛ̀lɛ̀] ", ""),
            ('\u0008', ''),
            ('\u030ct', 't'),
            ('#', ''), 
            ('"', ''),
            (" → ", " "),
            ("ⁿ ~ wⁿ (human)", ""),
            ("\u030ck", "k"),
            ("\u030cd", "d"),
            ("jògù dùyé ` dónì", "jògù dùyé dónì"),
            (" PRON ", ""),
            (' ', '_'),
            ],  # replacements with spaces
    )
    
    def cmd_download(self, args):

        URL = "https://github.com/clld/dogonlanguages-data/raw/master/beta/Dogon.comp.vocab.UNICODE-2017.xls"
        self.raw_dir.download(URL, "Dogon.comp.vocab.UNICODE-2017.xls")
        self.raw_dir.xls2csv("Dogon.comp.vocab.UNICODE-2017.xls")
        #lexicon = self.raw_dir.read_csv("Dogon.comp.vocab.UNICODE-2017.lexicon.csv")
        #concepts = sorted(set([(row[14], row[15], row[7], row[8], row[0]+'/'+row[1],
        #    row[2]+'/'+row[3]) for row in lexicon]))
        #with open(self.etc_dir.joinpath("concepts-new.tsv"), "w", encoding="utf-8") as f:
        #    f.write("NUMBER\tENGLISH\tFRENCH\tENGLISH_SHORT\tFRENCH_SHORT\tENGLISH_CATEGORY\tFRENCH\tCATEGORY\n")
        #    for i, row in enumerate(concepts):
        #        f.write(str(i+1)+'\t'+'\t'.join(row)+"\n")
        #with open(self.etc_dir.joinpath("languages-new.tsv"), "w") as f:
        #    f.write("ID\tLANGUAGE\n")
        #    for language in lexicon[0][17:43]:
        #        f.write(slug(language, lowercase=False)+"\t"+language+"\n")


    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """

        # Write source
        args.writer.add_sources()

        # Write languages
        args.writer.add_languages()

        # Write concepts
        concepts = {}
        for concept in self.concepts:
            if concept['CONCEPTICON_GLOSS'] != "THANK (SOMEBODY)":
                idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
                args.writer.add_concept(
                        ID=idx,
                        Name=concept['ENGLISH'],
                        PartOfSpeech=concept['POS'],
                        Concepticon_ID=concept["CONCEPTICON_ID"],
                        Concepticon_Gloss=concept["CONCEPTICON_GLOSS"]
                        )
                concepts[concept['ENGLISH'].replace('"', '')] = idx

        # Write forms
        lexicon = self.raw_dir.read_csv("Dogon.comp.vocab.UNICODE-2017.lexicon.csv",
                dicts=True)
        missing = set()
        for row in progressbar(lexicon, desc="cldfify"):
            concept = row["English"].replace('"', '')
            if concept not in concepts:
                missing.add(concept)
            else:
                for language in self.languages:
                    lid, lname = language["ID"], language["NameInSource"]
                    entry = row[lname].replace('-', '').strip()
                    if entry and entry[0] in "([{" and entry[-1] in ")]}":
                        continue
                    elif entry in ["ⁿ ~ wⁿ (human)", 
                            "→ (prolongation, final Htone)",
                            ": (length, falling tone)",
                            "[ǹdò ŋ̀gá] ... wɔ́",
                            "(floating L) X",
                            "[kú ôm] X wǒ",
                            "[ú yà→] [bírɛ́ yà→], [bìrɛ̀ wó] pǒ:",
                            "[bɛ̀nnà: íŋ]̀ nì:",
                            "X yà Y yà",
                            "X=: (length)",
                            "→ (vowel prolongation, rising pitch)",
                            " ̀(final Ltone)",
                            "[X lè] Y tégé",
                            "(jɛ̀mbɛ)̀ bálàlù",
                            "(nàmà)̀ kíndɛ́",
                            "V gɛ díɛ́", 
                            "(sɔ̀w yàa)̀ jíbú, yàà jìbé",
                            'sɔ̀: [kû: sɛ̀lɛ̀] [dúlɔ̀ sɛ̀lɛ̀] ("talk without a head or a tail")', 
                            "=∴",
                            "N",
                            "\u0060",
                            "\u0060(final Ltone)",
                            "[X jɛ́ nɛ̀] X",
                            "ADJ, ADJ=ẃ (Inan), ADJ=ŋ́ (AnSg), ADJ=yɛ́ (AnPl)",
                            "Y [X bày] kíyɛ́",
                            "ní: ! nì:",
                            "hàlí ... [X là] ... (mɛ̀)",
                            "[X dá:rú] Y sà",
                            "{L} after Lfinal pronoun or " 
                            "undetermined noun, {HL} after others",
                            "mì X=:",
                            ] or "VERB" in entry or "{L}, Astem)" in entry or \
                                    "final Ltone" in entry or "..." in entry \
                                    or "…" in entry or "∅" in entry or "X" in \
                                    entry or "VERB" in entry:
                        continue
                    if entry:
                        args.writer.add_forms_from_value(
                                Value=entry,
                                Language_ID=lid,
                                Parameter_ID=concepts[concept.replace('"', '')],
                                Source='heathdogon'
                                )
        for m in missing:
            args.log.info("MISSING CONCEPT: {0}".format(m))


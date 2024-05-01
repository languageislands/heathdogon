from pathlib import Path
from clldutils.misc import slug
from pylexibank import FormSpec, Lexeme, Concept, Language, Lexeme
from pylexibank import Dataset as BaseDataset
from pylexibank import progressbar
from lingpy import *
import attr
from unicodedata import normalize

@attr.s
class CustomConcept(Concept):
    PartOfSpeech = attr.ib(default=None)
    Swadesh = attr.ib(default=None)
    IDS_Gloss = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)
    NameInSource = attr.ib(default=None)


@attr.s
class CustomLexeme(Lexeme):
    Grouped_Segments = attr.ib(
            default=None,
            metadata={"datatype": "string", "separator": " "}
            )
    Dialect = attr.ib(default=None)
    Numerus = attr.ib(default=None)
    Lexeme_ID = attr.ib(default=None)


def ungroup(sounds):
    out = []
    for segment in sounds:
        if "." in segment:
            out += segment.split(".")
        else:
            out += [segment]
    return out


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "heathdogon"
    language_class = CustomLanguage
    concept_class = CustomConcept
    lexeme_class = CustomLexeme
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

        url = "https://github.com/clld/dogonlanguages-data/raw/master/beta/Dogon.comp.vocab.UNICODE-2017.xls"
        self.raw_dir.download(url, "Dogon.comp.vocab.UNICODE-2017.xls")
        self.raw_dir.xls2csv("Dogon.comp.vocab.UNICODE-2017.xls")

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """
        # select IDS concept list to check for concepts to be added
        ids = {c.concepticon_gloss: c.english for c in
                self.concepticon.conceptlists["Key-2016-1310"].concepts.values() if
                c.concepticon_gloss}
        # select only swadesh 207 terms (Comrie's list combining Swadesh 100
        # and Swadesh 200)
        swadesh = {c.concepticon_gloss for c in 
                   self.concepticon.conceptlists["Comrie-1977-207"].concepts.values()}

        # Write source
        args.writer.add_sources()

        # Write languages
        args.writer.add_languages()


        # check for manually separated cases
        language_mapper = {
                "BonduSoNajamba": "Najamba",
                "JamsayGourou": "Gourou",
                "TiranigeBuoi": "Tiranige",
                "TiranigeNingo": "Tiranige",
                }

        manual = {}
        for i, row in enumerate(
                self.raw_dir.read_csv("manually-edited.csv", dicts=True)):
            if row["SINGULAR"]:
                form = normalize("NFD", row["SINGULAR"]).replace("-", "")
            elif row["FORM"]:
                form = normalize("NFD", row["FORM"]).replace("-", "")
            else:
                args.log.info("No form found in linne {0} (ID: {1})".format(
                    i, row["ID"]))
                form = ""
            manual[
                    language_mapper.get(
                        row["DOCULECT"], 
                        row["DOCULECT"]),
                    row["GLOSS"], 
                    form
                    ] = row

        # Write concepts
        concepts = {}
        for concept in self.concepts:
            if concept['CONCEPTICON_GLOSS'] in ids:
                idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
                if concept["CONCEPTICON_GLOSS"] in swadesh:
                    swad = "1"
                else:
                    swad = "0"
                args.writer.add_concept(
                        ID=idx,
                        Name=concept['ENGLISH'],
                        PartOfSpeech=concept['POS'],
                        Concepticon_ID=concept["CONCEPTICON_ID"],
                        Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                        Swadesh=swad,
                        IDS_Gloss=ids[concept["CONCEPTICON_GLOSS"]]
                        )
                concepts[concept['ENGLISH'].replace('"', '')] = idx

        # Write forms
        lexicon = self.raw_dir.read_csv("Dogon.comp.vocab.UNICODE-2017.lexicon.csv",
                dicts=True)
        missing = set()
        missing_values = set()
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
                        if entry in self.lexemes:
                            entry = self.lexemes[entry]
                        forms = self.form_spec.split(
                                self.form_spec.separators,
                                entry)
                        if forms:
                            form = forms[0]
                            form = self.form_spec.clean(form)
                            for s, t in self.form_spec.replacements:
                                form = form.replace(s, t)
                            segments = self.tokenizer({}, form)
                            variety = ""
                            if "Boui" in entry:
                                variety = "Boui"
                            elif "Ningo" in entry:
                                variety = "Ningo"
                            
                            # check for match in the manually edited file
                            simple_form = normalize(
                                    "NFD", form.replace("-", "").replace("_", " "))
                            if (lid, concept, simple_form) not in manual:
                                missing_values.add((lid, concept, simple_form))

                            args.writer.add_form_with_segments(
                                    Language_ID=lid,
                                    Parameter_ID=concepts[concept.replace('"',
                                                                          '')],
                                    Value=entry,
                                    Form=form,
                                    Segments=ungroup(segments),
                                    Grouped_Segments=segments,
                                    Source="heathdogon")

                        #for lex in args.writer.add_forms_from_value(
                        #        Value=entry,
                        #        Language_ID=lid,
                        #        Parameter_ID=concepts[concept.replace('"', '')],
                        #        Source='heathdogon'
                        #        ):
                        #    lex["Grouped_Segments"] = lex["Segments"]
                        #    lex["Segments"] = ungroup(lex["Segments"])
        args.log.info("ignoring deliberately {0} rows".format(len(missing)))
        for a, b, c in missing_values:
            print(a, b, c)
        print(len(missing_values))

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
class CustomLexeme(Lexeme):
    Reflex_ID = attr.ib(default=None)

@attr.s
class CustomLanguage(Language):
    SubGroup = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "heathdogon"
    lexeme_class = CustomLexeme
    language_class = CustomLanguage
    concept_class = CustomConcept

    # define the way in which forms should be handled
    form_spec = FormSpec(
        brackets={"(": ")"},  # characters that function as brackets
        separators=";/,&~",  # characters that split forms e.g. "a, b".
        missing_data=("?", "-"),  # characters that denote missing data.
        strip_inside_brackets=True,  # do you want data removed in brackets?
        first_form_only=True,  # We ignore all the plural forms
        replacements=[(' ', '_')],  # replacements with spaces
    )

    def cmd_makecldf(self, args):
        """
        Convert the raw data to a CLDF dataset.
        """

        # Write source
        args.writer.add_sources()

        # Write languages
        languages = args.writer.add_languages(lookup_factory="Name")

        # Write concepts
        concepts = {}
        for concept in self.concepts:
            idx = concept['NUMBER']+'_'+slug(concept['ENGLISH'])
            args.writer.add_concept(
                    ID=idx,
                    Name=concept['ENGLISH'],
                    PartOfSpeech=concept['POS'],
                    )
            concepts[concept['ENGLISH']] = idx

        # Write forms
        wl = Wordlist(self.raw_dir.joinpath('data.tsv').as_posix())
        for idx in progressbar(wl):
            args.writer.add_forms_from_value(
                    Value=wl[idx, 'value'],
                    Language_ID=languages[wl[idx, 'doculect']],
                    Parameter_ID=concepts[wl[idx, 'concept']],
                    Source='heathdogon'
                    )


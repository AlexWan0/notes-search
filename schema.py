from whoosh.analysis import FancyAnalyzer, StemFilter, RegexTokenizer, NgramAnalyzer, NgramFilter, LanguageAnalyzer, LowercaseFilter
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, NUMERIC, NGRAMWORDS
from whoosh.analysis import StemmingAnalyzer, RegexTokenizer, NgramTokenizer

def create_whoosh(directory):
    subword_ngram = RegexTokenizer() | NgramFilter(1, 16) | LowercaseFilter()
    fancy = FancyAnalyzer() | StemFilter()

    schema = Schema(
        title=TEXT(stored=True, field_boost=3.0),
        url=TEXT(stored=True),
        line_num=NUMERIC(stored=True),
        contents_tokens=TEXT(analyzer=subword_ngram, field_boost=1.5),
        contents_subtokens=TEXT(analyzer=fancy, field_boost=1.0),
        arxiv_title=TEXT(analyzer=fancy, stored=True, field_boost=2.0),
        arxiv_authors=TEXT(analyzer=subword_ngram, stored=True, field_boost=3.0),
        arxiv_abstract=TEXT(analyzer=fancy, field_boost=0.5)
    )

    ix = create_in(directory, schema)

    return schema, ix


def load_whoosh(directory):
    ix = open_dir(directory)

    return ix

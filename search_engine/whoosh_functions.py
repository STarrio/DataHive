from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StemmingAnalyzer
from whoosh.writing import AsyncWriter

import os

whoosh_index = "whoosh_index"

def create_schema():
    if not os.path.exists(whoosh_index):
        os.mkdir(whoosh_index)

    schema = Schema(dataset_id=ID(stored=True),
                    abstract=TEXT(stored=True),
                    description=TEXT(analyzer=StemmingAnalyzer(), stored=True),
                    title=TEXT(stored=True))

    create_in(whoosh_index, schema)


def insert_docs(docs):
    ix = open_dir(whoosh_index)
    writer = AsyncWriter(ix)
    for doc in docs:
        writer.add_document(**doc)
    writer.commit()


def search_doc(txt):
    ix = open_dir(whoosh_index)

    with ix.searcher() as searcher:
        query = MultifieldParser(["description", "abstract", "title"], ix.schema).parse(txt)
        results = searcher.search(query, limit=20)
        results = [dict(r) for r in results]
    return results


def search_doc_by_id(id_):
    ix = open_dir(whoosh_index)

    with ix.searcher() as searcher:
        query = QueryParser("dataset_id", ix.schema).parse(str(id_))
        results = searcher.search(query)
        results = dict(results[0])

    return results

def get_three_like_this(id_):
    ix = open_dir(whoosh_index)

    with ix.searcher() as searcher:
        query = QueryParser("dataset_id", ix.schema).parse(str(id_))
        results = searcher.search(query)
        try:
            keys = results[0].more_like_this("description")[:3]
            keywords = [dict(k) for k in keys]
        except:
            keywords = None

    return keywords

def get_keywords_id(id_):
    ix = open_dir(whoosh_index)

    with ix.searcher() as searcher:
        query = QueryParser("dataset_id", ix.schema).parse(str(id_))
        results = searcher.search(query)
        try:
            keys = results.key_terms("abstract")
            keywords = [k[0] for k in keys][:3]
        except:
            keywords = ["No keywords"]

    return keywords


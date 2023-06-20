import pickle
import re
from tqdm import tqdm
import os
import shutil

from schema import create_whoosh
from notes_parse import build_hierarchy
from arxiv_api import ArxivBot
from utils import make_line_map, get_url
from config import papers_path

def run_update(verbose=False):
    # init files
    if not os.path.isdir("indexdir"):
        os.mkdir("indexdir")

    shutil.copyfile(papers_path, 'data/_papers.txt')


    # whoosh schema
    schema, ix = create_whoosh("indexdir")
    writer = ix.writer()


    # load data
    with open('data/_papers.txt') as f_in:
        raw_text = f_in.read()

    print('UPDATE: Parsing notes...')
    parsed_data = build_hierarchy(raw_text, verbose=verbose)


    # init arxiv bot
    arxiv_bot = ArxivBot()

    if os.path.isfile('data/arxiv_cache.json'):
        arxiv_bot.load_cache('data/arxiv_cache.json')


    # build index
    print('UPDATE: Building index...')

    for top_level in tqdm(parsed_data.children):
        notes_title = top_level.get_tree(depth=0)
        contents = top_level.get_tree()

        arxiv_title, authors, abstract = arxiv_bot.get_info(notes_title)
        
        arxiv_title = re.sub(r'\s{2,}', ' ', arxiv_title.strip()) if arxiv_title is not None else None
        
        writer.add_document(
            title=notes_title,
            url=get_url(notes_title),
            contents_tokens=contents,
            contents_subtokens=contents,
            line_num=top_level.line_idx,
            arxiv_title=arxiv_title,
            arxiv_authors=', '.join(authors) if authors is not None else None,
            arxiv_abstract=abstract.strip() if abstract is not None else None
        )

    writer.commit()

    arxiv_bot.dump_cache('data/arxiv_cache.json')

    ix.close()


    # map from line idx to hierarchy nodes
    line_to_node = make_line_map(parsed_data)


    # save data
    with open('data/line_map.pkl', 'wb') as f_out:
        pickle.dump(line_to_node, f_out)

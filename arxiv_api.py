import xml.etree.ElementTree as ET
import requests
import re
import json
import os


CACHE_FN = 'data/arxiv_cache.json'


def get_cached_bot(cache_fn=CACHE_FN):
    bot = ArxivBot()

    if os.path.isfile(cache_fn):
        bot.load_cache(cache_fn)

    return bot


def get_paper_info(paper_id):
    # by chatgpt

    url = f"http://export.arxiv.org/api/query?id_list={paper_id}"
    response = requests.get(url)

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        entry = root.find("{http://www.w3.org/2005/Atom}entry")

        title = entry.find("{http://www.w3.org/2005/Atom}title").text

        authors = []
        for author in entry.findall("{http://www.w3.org/2005/Atom}author"):
            name = author.find("{http://www.w3.org/2005/Atom}name").text
            authors.append(name)

        abstract = entry.find("{http://www.w3.org/2005/Atom}summary").text

        return title, authors, abstract
    else:
        return None

arxiv_id_abs = r'((pdf)|(abs))\/(\d{4}\.\d{5})\/?(\.pdf)?\/?'

class ArxivBot:
    def __init__(self):
        self.cache = {}

    def get_arxiv_id(self, title_raw):
        re_match = re.search(arxiv_id_abs, title_raw)

        if re_match is None:
            return None

        return re_match.group(4)
    
    def load_cache(self, fn):
        with open(fn) as f_in:
            self.cache = json.load(f_in)
    
    def dump_cache(self, fn=CACHE_FN):
        with open(fn, 'w') as f_out:
            json.dump(self.cache, f_out)
    
    def arxiv_info_cached(self, arxiv_id):
        if arxiv_id in self.cache:
            return self.cache[arxiv_id]

        title, authors, abstract = get_paper_info(arxiv_id)

        self.cache[arxiv_id] = (title, authors, abstract)

        return (title, authors, abstract)

    def get_info(self, title_raw):
        arxiv_id = self.get_arxiv_id(title_raw)

        if arxiv_id is None:
            return None, None, None
        
        return self.arxiv_info_cached(arxiv_id)
    
    def _get_arxiv_link_replacement(self, re_match):
        arxiv_id = re_match.group(4)

        (title, authors, _) = self.arxiv_info_cached(arxiv_id)

        full_matched = re_match.group()

        author_str = ', '.join(authors)

        title = re.sub(r'\s+', ' ', title)

        return f'{full_matched} [["{title}" by {author_str}]]'

    def replace_info(self, text_raw):
        regex = re.compile(arxiv_id_abs)

        matches = regex.finditer(text_raw)

        for match in matches:
            replacement = self._get_arxiv_link_replacement(match)
            text_raw = text_raw.replace(match.group(), replacement)

        return text_raw

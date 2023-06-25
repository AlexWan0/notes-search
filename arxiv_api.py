import xml.etree.ElementTree as ET
import requests
import re
import json


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
    
    def dump_cache(self, fn):
        with open(fn, 'w') as f_out:
            json.dump(self.cache, f_out)
    
    def get_info(self, title_raw, delay=0.1):
        arxiv_id = self.get_arxiv_id(title_raw)

        if arxiv_id is None:
            return None, None, None
        
        if arxiv_id in self.cache:
            return self.cache[arxiv_id]
        
#         res = requests.get(abs_link, headers=simple_headers)
#         time.sleep(delay)
        
#         html = bs4.BeautifulSoup(res.text)

#         page_title = html.title.text.strip()

        title, authors, abstract = get_paper_info(arxiv_id)

        self.cache[arxiv_id] = (title, authors, abstract)
        
        return (title, authors, abstract)

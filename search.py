from whoosh.qparser import MultifieldParser
import pickle
import time
from colors import color
import sys

from schema import load_whoosh

# query_raw = sys.argv[1]

# print(color('query: ' + query_raw, 'red'))

class Search:
    def __init__(self):
        # load data
        with open('data/line_map.pkl', 'rb') as f_in:
            self.line_to_node = pickle.load(f_in)

        # whoosh schema
        self.ix = load_whoosh("indexdir")

    def do_search(self, query_raw):
        # do search
        with self.ix.searcher() as searcher:
            query = MultifieldParser(
                [
                    'contents_tokens',
                    'contents_subtokens',
                    'title',
                    'arxiv_title',
                    'arxiv_authors',
                    'arxiv_abstract'
                ],
                schema=self.ix.schema
            ).parse(query_raw)

            start = time.time()
            results = searcher.search(query)
            print(color('latency: %.4f' % (time.time() - start), 'red') + '\n')

            result_format = []

            for res in results:
                print(color(res['title'], 'green', style='bold'))

                if 'arxiv_title' in res:
                    print(color(res['arxiv_title'], 'blue', style='bold'))

                if 'arxiv_authors' in res:
                    print(color(res['arxiv_authors'], 'blue', style='bold'))

                contents = self.line_to_node[res['line_num']].get_tree()
                contents_body = '\n'.join(contents.split('\n')[1:])
                
                print(contents_body)

                print('-' * 25)

                row_format = [
                    res['title'],
                    res['arxiv_title'] if 'arxiv_title' in res else None,
                    res['arxiv_authors'] if 'arxiv_authors' in res else None,
                    contents_body
                ]

                result_format.append(row_format)
            
            return result_format

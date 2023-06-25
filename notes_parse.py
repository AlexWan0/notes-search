import itertools
from collections import namedtuple
from colors import color
from typing import TypeVar
from arxiv_api import get_cached_bot


INDENT_CHAR = '\t'


# can't do self-reference types :(
TLine = TypeVar("TLine", bound="Line")

class Line:
    ROOT = '_root'
    EMPTY = '_empty'
    
    def __init__(self, level: int, contents: str, children: list[TLine], parent: TLine, line_idx: int):
        self.level = level
        self.contents = contents
        self.children = children
        self.parent = parent
        self.line_idx = line_idx
    
    @classmethod
    def make_root(cls) -> TLine:
        return Line(-1, Line.ROOT, [], None, None)
    
    def add_child(self, contents, line_idx) -> TLine:
        new_node = Line(self.level + 1, contents, [], self, line_idx)
        self.children.append(new_node)
        return new_node
    
    def add_sibling(self, contents, line_idx) -> TLine:
        new_node = Line(self.level, contents, [], self.parent, line_idx)
        self.parent.children.append(new_node)
        return new_node
    
    def get_tree(self, indent_char='\t', depth=None) -> str:
        if depth is not None and depth > 0:
            recurse = '\n'.join([child.get_tree(indent_char=indent_char, depth=(depth - 1)) for child in self.children])
        elif depth is None:
            recurse = '\n'.join([child.get_tree(indent_char=indent_char, depth=None) for child in self.children])
        else:
            recurse = ''
        
        if len(recurse) > 0:
            recurse = '\n' + recurse
        
        prefix = indent_char * self.level
        
        return prefix + self.contents + recurse


get_cached_bot

def add_arxiv_to_content(content)


def build_hierarchy(raw_text: str, verbose=False) -> Line:
    parsed_data = Line.make_root()

    curr_pointer = parsed_data

    for line_idx, line in enumerate(raw_text.split('\n')):
        if verbose:
            print('--')
        
        if len(line.strip()) == 0:
            if verbose:
                print(color('SKIP EMPTY LINE', 'red'))

            continue

        num_leading = sum(1 for _ in itertools.takewhile(lambda ch: ch == INDENT_CHAR, line))
        
        if verbose:
            print(color('num_leading: %d, curr: %d' % (num_leading, curr_pointer.level), 'blue'))
            print(line)
        
        if num_leading > curr_pointer.level:
            # keep making nested lists until we reach (our target level - 1)
            while (num_leading - 1) > curr_pointer.level:
                if verbose:
                    print(color('PAD UP ONE', 'green'))
                
                curr_pointer = curr_pointer.add_child(Line.EMPTY, None)
            
            if verbose:
                print(color('GO UP ONE', 'green'))
                print(color('adding child at level: %d' % (curr_pointer.level + 1), 'blue'))
                
            assert (curr_pointer.level + 1) == num_leading
            
            curr_pointer = curr_pointer.add_child(line.strip(), line_idx)
            
            continue
        
        if num_leading < curr_pointer.level:
            for _ in range(curr_pointer.level - num_leading):
                if verbose:
                    print(color('GO DOWN ONE', 'green'))
                
                curr_pointer = curr_pointer.parent
        
        assert num_leading == curr_pointer.level
        
        if verbose:
            print(color('adding sibling at level: %d' % curr_pointer.level, 'blue'))
        
        curr_pointer = curr_pointer.add_sibling(line.strip(), line_idx)
    
    return parsed_data

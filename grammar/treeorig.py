from graphviz import Digraph
from typing import Callable, Any, Tuple, List
import re
import string

# Helper functions
def dot_escape(s: str, show_ascii=None) -> str:
    escaped_s = ''
    show_ascii = show_ascii if show_ascii is not None else (len(s) == 1)
    if show_ascii and s == '\n':
        return '\\\\n (10)'
    s = s.replace('\n', '\\n')
    for c in s:
        if re.match('[,<>\\\\"]', c):
            escaped_s += '\\' + c
        elif c in string.printable and 31 < ord(c) < 127:
            escaped_s += c
        else:
            escaped_s += '\\\\x' + format(ord(c), '02x')
        if show_ascii:
            escaped_s += f' ({ord(c)})'
    return escaped_s

def extract_node(node, id):
    symbol, children, *annotation = node
    return symbol, children, ''.join(str(a) for a in annotation)

def default_node_attr(dot, nid, symbol, ann):
    dot.node(repr(nid), dot_escape(symbol))

def default_edge_attr(dot, start_node, stop_node):
    dot.edge(repr(start_node), repr(stop_node))

def default_graph_attr(dot):
    dot.attr('node', shape='plain')

# The display_tree function
def display_tree(derivation_tree: Tuple[str, List[Any], Any],
                 log: bool = False,
                 extract_node: Callable = extract_node,
                 node_attr: Callable = default_node_attr,
                 edge_attr: Callable = default_edge_attr,
                 graph_attr: Callable = default_graph_attr) -> Digraph:
    counter = 0

    def traverse_tree(dot, tree, id=0):
        nonlocal counter
        symbol, children, annotation = extract_node(tree, id)
        node_attr(dot, id, symbol, annotation)
        if children:
            for child in children:
                counter += 1
                child_id = counter
                edge_attr(dot, id, child_id)
                traverse_tree(dot, child, child_id)

    dot = Digraph(comment="Derivation Tree")
    graph_attr(dot)
    traverse_tree(dot, derivation_tree)
    if log:
        print(dot)
    return dot


__all__ = ['doc_tag' ] 

import functools
import builtins
import numpy as np
import datascience

_root = "http://cs.williams.edu/~cs104/auto/python-library-ref.html"

def url(tag):
    return _root + "#" + tag

def doc_tag(tag=None):
    def decorator_tag(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if tag is None:
                __doc_url__ = url(func.__name__)
            else:
                __doc_url__ = url(tag)
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_tag

libs_to_wrap = [
    (builtins, [ 
        'abs',
        'all',
        'any',
        'len',
        'max',
        'min',
        'pow',
        'round',
        'sorted',
        'sum' ]),
    (np, [
        'max',
        'min',
        'sum',
        'abs',
        'round',
        'mean',
        'average',
        'diff',
        'sqrt',
        'arange',
        'count_nonzero',
        'append',
        'percentile',
        'std']),
    (datascience.Table, [
        ('__init__', 'Table'),
        'read_table',
        'with_columns',
        'column',
        'select',
        'drop',
        'relabeled',
        'show',
        'sort',
        'where',
        'take',
        'take_clean',
        'take_messy',
        'scatter',
        'plot',
        'barh',
        'hist',
        'bin',
        'apply',
        'group',
        'pivot',
        'join',
        'sample',
        'row'
    ]),
    (datascience, [
        'make_array',
        'percentile',
        'sample_proportions',
        'minimize'
    ]),
    (datascience.Plot, [
        'dot',
        'square',
        'interval',
        'line',
        ('set_title', 'set-labels'),
        ('set_ylabel', 'set-labels'),
        ('set_xlabel', 'set-labels'),
        ('set_ylim', 'set-limits'),
        ('set_xlim', 'set-limits')
    ]),
    (np.random, [
        'choice'
    ]),
]

def _wrapper(tag, func): 
    def call(*args, **kwargs):
        __doc_url__ = url(tag)
        result = func(*args, **kwargs)
        return result
    return call

for module, fns in libs_to_wrap:
    for fn in fns:
        if type(fn) == str:
            setattr(module, fn, _wrapper(fn, module.__dict__[fn]))
        else:
            fn, tag = fn
            setattr(module, fn, _wrapper(tag, module.__dict__[fn]))

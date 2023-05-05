
__all__ = [ 'doc_tag' ] 

import functools
import builtins
import numpy as np
import datascience

# _root = "http://cs.williams.edu/~cs104/auto/python-library-ref.html"
_root = "https://cs104williams.github.io/assets/python-library-ref.html"

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
        ('read_table','read_table',True),
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

def _wrapper(tag, fn_name, func): 
    def call(*args, **kwargs):
        __doc_url__ = url(tag)  # special name picked up in cs104.exceptions.
        return func(*args, **kwargs)
    
    wrapper = call
    wrapper.__name__ = fn_name
    return wrapper

def _wrapper_static(tag, fn_name, module, func): 
    @classmethod
    def call(*args, **kwargs):
        __doc_url__ = url(tag)   # special name picked up in cs104.exceptions.
        return func.__get__(args[0],module)(*args[1:], **kwargs)
    
    wrapper = call
    wrapper.__name__ = fn_name
    return wrapper

for module, fn_names in libs_to_wrap:
    for fn_name in fn_names:
        if type(fn_name) == str:
            # tag is same as function name
            original_function = module.__dict__[fn_name]
            wrapper = _wrapper(fn_name, fn_name, original_function)
        elif len(fn_name) == 2: 
            # tag is different than function name
            fn_name, tag = fn_name
            original_function = module.__dict__[fn_name]
            wrapper = _wrapper(tag, fn_name, original_function)
        else:
            # function may be a static method
            fn_name, tag, is_static = fn_name
            original_function = module.__dict__[fn_name]
            if is_static:
                wrapper = _wrapper_static(tag, fn_name, module, original_function)
            else: 
                wrapper = _wrapper(tag, fn_name, original_function)

        setattr(module, fn_name, wrapper)

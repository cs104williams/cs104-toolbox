"""
A package to tie library functions to their documentation entries.
This is used to generate links in error messages to the webpage
that decribes the offending function.  This code works in 
conjunction with exception.py.

Most of the datascience and np library functions we use are baked 
into this module.  If there are others, use the `@doc_tag` 
decoration to connect a function to its documentation tag.

"""

__all__ = []

import functools
import builtins
import numpy as np
import datascience

# The URL of the docs page -- use the indirect on github to avoid
# being dependent on where the local pages are installed...

# The url except for the last bit
_root = "https://cs104williams.github.io/assets/"

# The main doc page -- this is separate so we can override it with tags
#  for special pages like the inference page.
_path = "python-library-ref.html"

# All of the library functions we want to link to the docs.
_libs_to_wrap = [
    (
        builtins,
        ["abs", "all", "any", "len", "max", "min", "pow", "round", "sorted", "sum"],
    ),
    (
        np,
        [
            "max",
            "min",
            "sum",
            "abs",
            "round",
            "mean",
            "average",
            "diff",
            "sqrt",
            "arange",
            "count_nonzero",
            "append",
            "percentile",
            "std",
        ],
    ),
    (
        datascience.Table,
        [
            ("__init__", "Table"),
            ("read_table", "read_table", True),
            "with_columns",
            "column",
            "select",
            "drop",
            "relabeled",
            "show",
            "sort",
            "where",
            "take",
            "take_clean",
            "take_messy",
            "scatter",
            "plot",
            "barh",
            "hist",
            "bin",
            "apply",
            "group",
            "pivot",
            "join",
            "sample",
            "row",
        ],
    ),
    (datascience, ["make_array", "percentile", "sample_proportions", "minimize"]),
    (
        datascience.Plot,
        [
            "dot",
            "square",
            "interval",
            "line",
            ("set_title", "set-labels"),
            ("set_ylabel", "set-labels"),
            ("set_xlabel", "set-labels"),
            ("set_ylim", "set-limits"),
            ("set_xlim", "set-limits"),
        ],
    ),
    (np.random, ["choice"]),
]


def _url(path=None, tag=None):
    """Build a URL out of the root, the path, and a function's tag"""
    if path == None:
        path = _path
    if tag != None:
        return _root + path + "#" + tag
    else:
        return _root + path


def doc_tag(tag=None, path=None):
    """
    A function decorator that ties a function to the given tag
    on the documentation page.
    """

    def decorator_tag(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if tag is None:
                __doc_url__ = _url(path=path, tag=func.__name__)
            else:
                __doc_url__ = _url(path=path, tag=tag)
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator_tag


def _wrapper(tag, fn_name, func):
    """The basic wrapper for a library function"""

    def call(*args, **kwargs):
        __doc_url__ = _url(tag=tag)  # special name picked up in cs104.exceptions.
        return func(*args, **kwargs)

    wrapper = call
    wrapper.__name__ = fn_name
    wrapper.__doc__ = func.__doc__
    return wrapper


def _wrapper_static(tag, fn_name, module, func):
    """The wrapper for a static library function"""

    @classmethod
    def call(*args, **kwargs):
        __doc_url__ = _url(tag=tag)  # special name picked up in cs104.exceptions.
        return func.__get__(args[0], module)(*args[1:], **kwargs)

    wrapper = call
    wrapper.__name__ = fn_name
    wrapper.__doc__ = func.__doc__
    return wrapper


# Iterate over all functions to wrap, calling the appropriate
# wrapper function on each.
for module, fn_names in _libs_to_wrap:
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

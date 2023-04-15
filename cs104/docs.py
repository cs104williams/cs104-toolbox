
# __all__ = [ "ValueError" ]

# _root = "http://cs.williams.edu/~cs104/auto/python-library-ref.html"

# class ValueError(Exception):
#     def __init__(self, message, link = None):
#         self.message = message
#         self.link = link
        
#     def __str__(self):
#         if self.link is not None:
#             tail = f"\n\n\u001b[1mSee also:\u001b[0m{_root}#{self.link}\n  "
#         else:
#             tail = ""
#         return self.message + tail

import functools

def doc_tag(tag=None):
    def decorator_tag(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if tag is None:
                __doc_tag__ = func.__name__
            else:
                __doc_tag__ = tag
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_tag

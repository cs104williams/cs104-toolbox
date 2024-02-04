
__all__ = [ 'doc_tag' ] 

def doc_tag(tag=None, path=None):
    def decorator_tag(func):
        return func
    return decorator_tag
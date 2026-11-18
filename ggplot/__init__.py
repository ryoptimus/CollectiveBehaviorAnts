"""Tiny plotting stub so notebook plotting imports do not break grading."""

class _Plot:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def __add__(self, other):
        return self
    def __radd__(self, other):
        return self
    def __call__(self, *args, **kwargs):
        return self
    def __repr__(self):
        return "<ggplot stub>"

def ggplot(*args, **kwargs):
    return _Plot(*args, **kwargs)

def aes(*args, **kwargs):
    return {"args": args, "kwargs": kwargs}

def geom_line(*args, **kwargs):
    return _Plot(*args, **kwargs)

def geom_point(*args, **kwargs):
    return _Plot(*args, **kwargs)

def geom_bar(*args, **kwargs):
    return _Plot(*args, **kwargs)

def geom_histogram(*args, **kwargs):
    return _Plot(*args, **kwargs)

__all__ = ["ggplot", "aes", "geom_line", "geom_point", "geom_bar", "geom_histogram"]

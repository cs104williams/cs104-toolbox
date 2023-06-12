__all__ = [ 'interact', 'Fixed', 'CheckBox', 'Text', 'Slider', 'Choice', 'record' ] 
           
from IPython.display import display
import ipywidgets
import numpy as np


from .docs import doc_tag
import inspect

class Control: 
    def __str__(self):
        return str(self._v)

class Fixed(Control):
    def __init__(self, value=None):
        self._v = ipywidgets.interaction.fixed(value)

class CheckBox(Control):
    def __init__(self, initial=None):
        self._v = True if initial is None else initial

class Text(Control):
    def __init__(self, initial = "<enter text>"):
        self._v = initial

class Slider(Control):
    @doc_tag('interact')
    def __init__(self, *args):
        if np.shape(args) == (1,2) or np.shape(args) == (1,3):
            args = args[0]
        if np.shape(args) != (2,) and np.shape(args) != (3,):
            raise ValueError(f"{args} is not a valid range for a Slider.")
        
        self._v = args

class Choice(Control):
    @doc_tag('interact')
    def __init__(self, *args):
        if len(args) == 1 and np.shape(args[0]) != ():
            args = args[0]
        self._v = list(args)
    
def make_widgets(f, kwargs):
    parameter_names = inspect.signature(f).parameters.keys()
    
    missing = [p for p in parameter_names if p not in kwargs] 
    if missing != []:
        raise ValueError(f"Missing arguments to interact: {', '.join(missing)}.  You must provide an argument for each parameter of {f.__name__}.")
    
    widgets = dict()
    
    for param, value in kwargs.items():
        if issubclass(type(value), Control):
            widgets[param] = value._v
        else:
            raise ValueError(f"Parameter for {param} is not a control -- did you mean {param}=Fixed(...)?")
    
    return widgets

@doc_tag('interact')
def interact(f, **kwargs):
    widgets = make_widgets(f, kwargs)
    ipywidgets.interact(f, **widgets)

def record(f, **kwargs):
    widgets = make_widgets(f, kwargs)
    interactor = ipywidgets.interactive(f, **widgets)
    
    controls = interactor.children[:-1]
    out = ipywidgets.Textarea(f"def gen():\n    pass\n", layout=ipywidgets.Layout(width='100%', height="200px"))
    interactor.children = (ipywidgets.Text(value='', description='_caption'),) + interactor.children + (out,)
    
    def changed(change):
        args = "; ".join([ f'{c.description} = {repr(c.value)}' for c in controls ])
        out.value = out.value.replace("    pass\n", f"    {args}\n    yield locals()\n    pass\n")
            
    for child in controls:
        child.observe(changed, names='value')
        
    changed(None)

    display(interactor)


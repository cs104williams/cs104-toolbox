__all__ = [ 'interact', 'CheckBox', 'Text', 'Slider', 'Choice' ] 
           
from IPython.display import display
from ipywidgets import interactive, Text, interaction
import numpy as np

from .docs import doc_tag
import inspect

class Control: 
    def __str__(self):
        return str(self._v)

class CheckBox(Control):
    def __init__(self, initial=None):
        self._v = True if initial is None else initial

class Text(Control):
    def __init__(self, initial = "<enter text>"):
        self._v = initial

class Slider(Control):
    @doc_tag('interact')
    def __init__(self, *args, step=None):
        if np.shape(args) == (1,2):
            args = args[0]
        elif np.shape(args) != (2,):
                raise ValueError("You must provide two numbers to create a slider. " +
                                 "Eg: Slider(lo,hi) or Slider(range) where a is an array [lo,hi].")
        if step != None:
            args = args + (step,)
            
        self._v = args

class Choice(Control):
    @doc_tag('interact')
    def __init__(self, *args):
        if len(args) == 1 and np.shape(args[0]) != ():
            args = args[0]
        self._v = list(args)
    
@doc_tag('interact')
def interact(f, **kwargs):
    parameter_names = inspect.signature(f).parameters.keys()
    
    missing = [p for p in parameter_names if p not in kwargs] 
    if missing != []:
        raise ValueError(f"Missing arguments to interact: {', '.join(missing)}.  You must provide an argument for each parameter of {f.__name__}.")
    
    widgets = dict()
    
    for param, value in kwargs.items():
        if issubclass(type(value), Control):
            widgets[param] = value._v
        else:
            widgets[param] = interaction.fixed(value)

    w = interactive(f, **widgets)
    display(w)



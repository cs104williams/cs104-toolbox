from IPython.display import HTML
from ipywidgets import interactive, Text, Textarea, Layout, interaction
from ipywidgets import interact as ipy_interact
import numpy as np

from .valueerror import *
import inspect

class Control: 
    def __str__(self):
        return str(self._v)

class Fixed(Control):
    def __init__(self, v):
        self._v = interaction.fixed(v)

class CheckBox(Control):
    def __init__(self, initial=None):
        self._v = True if initial is None else initial

class Text(Control):
    def __init__(self, initial = "<enter text>"):
        self._v = initial

class Slider(Control):
    def __init__(self, *args, step=None):
        print(np.shape(args))
        if np.shape(args) == (1,2):
            args = args[0]
        elif np.shape(args) != (2,):
                raise ValueError("You must provide two numbers to create a slider. " +
                                 "Eg: Slider(lo,hi) or Slider(range) where a is an array [lo,hi].", "column")
        if step != None:
            args = args + step
            
        self._v = args

class Choice(Control):
    def __init__(self, *args):
        if len(args) == 1 and np.shape(args[0]) != ():
            args = args[0]
        self._v = list(args)
    
def interact(f, **kwargs):
    parameter_names = inspect.signature(f).parameters.keys()
    
    missing = [p for p in parameter_names if p not in kwargs] 
    if missing != []:
        raise ValueError(f"Missing arguments to interact: {', '.join(missing)}.  You must provide an argument for each parameter of {f.__name__}.", "col")
    
    widgets = dict()
    
    for param, value in kwargs.items():
        if not issubclass(type(value), Control):
            raise ValueError(f"argment: {param} must be one of the interactive controls: Fixed(...), CheckBox(...), Slider(...), or Choice(...)", "col")
        widgets[param] = value._v
    ipy_interact(f, **widgets)


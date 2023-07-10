"""
Objects for creating interactive Visualizations.

The key function is `interact`, which is modeled after the underlying 
matplotlib function.  The `interact` function takes a function, and then
a list of keyword arges matching the parameter names for the function 
to Control objects, each of which describes how the user may adjust 
each parameter to the given function.
"""

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
    """
    A paramater with a fixed value.
    """
    def __init__(self, value=None):
        self._v = ipywidgets.interaction.fixed(value)

class CheckBox(Control):
    """
    An adjustable boolean parameter.  This parameter is
    displayed as a check box.
    """
    def __init__(self, initial=True):
        """
        initial is the beginning value for the parameter.
        The default is True.
        """
        self._v = initial

class Text(Control):
    """
    An adjustable text parameter.  This parameter is
    displayed as an editable text field.
    """
    def __init__(self, initial = "<enter text>"):
        """
        initial is the beginning text for the parameter.
        The default is a generic prompt.
        """
        self._v = initial

class Slider(Control):
    """
    An adjustable numerical parameter.  This parameter is 
    displayed as a slider.
    """
    @doc_tag('interact')
    def __init__(self, *args):
        """
        The initializer takes two or three parameters.  The first two
        are the lo and hi values for the range.  The optional third is
        the step size.

        Alternatively, pass in an array of two or three values with the
        same meaning as above. 
        """
        if np.shape(args) == (1,2) or np.shape(args) == (1,3):
            args = args[0]
        if np.shape(args) != (2,) and np.shape(args) != (3,):
            raise ValueError(f"{args} is not a valid range for a Slider.")
        
        self._v = args

class Choice(Control):
    """
    A parameter with discrete (non-numeric) values.  This parameter is 
    displayed as a popup menu.
    """

    @doc_tag('interact')
    def __init__(self, *args):
        """
        The initializer takes any number of values to use in the menu,
        or a single value containing and array of values to use.
        """
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
    """
    Create an interactive visualization.
    
    Parameters:
    - f: the function to visualize.  Most likely, f will create a plot
         or print some text.
    - kwargs: a list of parameters with the same names as f's parameters,
              each of which is set to a Control object.
              
    Example:

    def mult(x,y,z):
        print(x * y * z)
    
    interact(mult, x=Slider(0,10,0.5), y=Choice(1,2,4), z=Fixed(5))
    """
    widgets = make_widgets(f, kwargs)
    ipywidgets.interact(f, **widgets)

def record(f, **kwargs):
    """
    A helper to record interactions to make replaying with animations 
    easier.  You should only use this function for when setting up such
    an animation.  Generally, only `interact` is needed.
    """
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


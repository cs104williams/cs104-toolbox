from datascience import Plot
from matplotlib import pyplot as plots
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText
import numpy as np

from IPython.display import HTML
from ipywidgets import interact, interactive, Text, Textarea, Layout

import inspect
import numbers

def animate(f, gen, interval=200, **kwargs):

    kwargs = kwargs.copy()
    kwargs.setdefault('figsize', (10, 6))
    
    fig, ax = plots.subplots(**kwargs)

    parameter_names = inspect.signature(f).parameters.keys()

    def one_frame(args):
        ax.clear()
        
        parameters = {k: args[k] for k in parameter_names}
        
        np.random.seed(0) # make sort-of deterministic...
        
        f(**parameters)

        if '_caption' in args and args['_caption'] != "":
            caption = args['_caption'] 
            at = AnchoredText(caption, 
                              loc='upper center', 
                              prop=dict(size=16), 
                              frameon=True)
            at.set_zorder(40)
            ax.add_artist(at)
            at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
            at.patch.set_facecolor('yellow')

        if hasattr(f, '__name__'):
            name = f.__name__
        else:
            name = f.func.__name__
            parameters['...'] = '...'

        def r(v):
            if isinstance(v, numbers.Number):
                return round(v, 4)
            else:
                return v

        arg_values = f"{name}(\n  "  \
                    + f",\n  ".join([ f"{key} = {r(value)}" for key,value in sorted(parameters.items()) ]) \
                    + "\n)"
        at = AnchoredText(arg_values,
                          loc='upper left', 
                          prop=dict(size=14,fontfamily='sans-serif'), 
                          frameon=True,
                          bbox_to_anchor=(1.025, 0.5),
                          bbox_transform=ax.transAxes)
        ax.add_artist(at)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2") 
        at.patch.set_facecolor('wheat')


    with Plot(ax):
        anim = FuncAnimation(fig, func = one_frame, frames = gen, interval = interval)
        ax.get_figure().tight_layout(pad=2, rect=[0, 0, 0.75, 1])
        video = anim.to_jshtml()
        
    plots.close(fig)
    display(HTML(video))
    

def record(f, **kwargs):
    w = interactive(f, **kwargs)
    
    controls = w.children[:-1]
    out = Textarea(f"def gen():\n    pass\n", layout=Layout(width='100%', height="200px"))
    w.children = (Text(value='', description='_caption'),) + w.children + (out,)
    
    def changed(change):
        args = { c.description:c.value for c in controls }
        out.value = out.value.replace("    pass\n", f"    yield {args}\n    pass\n")
            
    for child in controls:
        child.observe(changed, names='value')
        
    changed(None)

    display(w)
from datascience import Plot
from matplotlib import pyplot as plots
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText
import numpy as np

from IPython.display import HTML

import inspect

def animate(f, gen, **kwargs):

    kwargs = kwargs.copy()
    kwargs.setdefault('figsize', (10, 6))
    
    fig, ax = plots.subplots(**kwargs)

    parameter_names = inspect.signature(f).parameters.keys()

    def one_frame(args):
        ax.clear()
        
        parameters = {k: args[k] for k in parameter_names}
        
        np.random.seed(0)
        f(**parameters)

        if '_caption' in args and args['_caption'] != "":
            caption = args['_caption'] 
            at = AnchoredText(caption, loc='upper center', prop=dict(size=16), frameon=True)
            ax.add_artist(at)
            at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
            at.patch.set_facecolor('yellow')

        arg_values = f"{f.__name__}(\n  " + f",\n  ".join([ f"{key} = {value}" for key,value in sorted(parameters.items()) ]) + "\n)"
        at = AnchoredText(arg_values,
                           loc='upper left', prop=dict(size=14,fontfamily='sans-serif'), frameon=True,
                           bbox_to_anchor=(1.025, 0.5),
                           bbox_transform=ax.transAxes)
        ax.add_artist(at)
        at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2") 
        at.patch.set_facecolor('wheat')


    with Plot(ax):
        anim = FuncAnimation(fig, func = one_frame, frames = gen, interval = 200)
        ax.get_figure().tight_layout(pad=2, rect=[0, 0, 0.75, 1])
        video = anim.to_jshtml()
        
    plots.close(fig)
    display(HTML(video))
    
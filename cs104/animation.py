from datascience import push_ax, pop_ax
from matplotlib import pyplot as plots
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText

from IPython.display import HTML

import inspect

def animate(f, gen, ax=None):
    if ax == None:
        _, ax = plots.subplots(figsize = (10, 6))

    parameter_names = inspect.signature(f).parameters.keys()

    def one_frame(args):
        ax.clear()
        
        parameters = {k: args[k] for k in parameter_names}
        
        f(**parameters)

        if 'title' in args and args['title'] != "":
            title = args['title'] 
            at = AnchoredText(title, loc='upper center', prop=dict(size=16), frameon=True)
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


    push_ax(ax)
    anim = FuncAnimation(fig = ax.get_figure(), func = one_frame, frames = gen, interval = 200)
    ax.get_figure().tight_layout(pad=2, rect=[0, 0, 0.75, 1])
    video = anim.to_jshtml()
    pop_ax()
    plots.close()
    display(HTML(video))


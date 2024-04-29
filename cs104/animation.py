__all__ = ["animate"]


import inspect
import numbers

import numpy as np
from datascience import Figure
from IPython.display import HTML, display
from matplotlib import pyplot as plots
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText


def animate(
    f, gen, interval=100, default_mode=None, fig=None, show_params=True, **kwargs
):
    """
    Animate a series of calls to the function f.  That function should create
    a single plot.

    The gen parameter should be a generator function that returns a map from f's
    parameters to their values.  Successive calls to gen returns the values for
    successive frames.  Optional arguments:

    * interval: the time step, in ms.
    * default_mode: the mode for the player.  Options are "Once", "Repeat, "Rewind".
    * fig: pass in a matplot lib Figure if you do not want the function to create
        a new figure for the animation.
    * show_params: Show the parameters to f in a box to the side of the figure.
    * **kwargs: Any additional kwargs are pass to the constructor for Figure.
        Requires fig to be None.
    """

    kwargs = kwargs.copy()
    kwargs.setdefault("figsize", (8, 5))

    if fig is None:
        fig = Figure(**kwargs)

    parameter_names = inspect.signature(f).parameters.keys()

    def one_frame(args):
        for ax in fig.axes():
            ax.clear()

        with fig:

            parameters = {k: args[k] for k in parameter_names}

            np.random.seed(0)  # make sort-of deterministic...

            f(**parameters)

            ax = fig.axes()[-1]

            if "_caption" in args and args["_caption"] != "":
                caption = args["_caption"]
                at = AnchoredText(
                    caption, loc="upper center", prop=dict(size=16), frameon=True
                )
                at.set_zorder(60)
                ax.add_artist(at)
                at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
                at.patch.set_facecolor("yellow")

            if show_params:
                if hasattr(f, "__name__"):
                    name = f.__name__
                else:
                    name = f.func.__name__
                    parameters["..."] = "..."

                def r(v):
                    if isinstance(v, numbers.Number):
                        s = str(round(v, 4))
                    elif isinstance(v, (str, bool)):
                        s = repr(v)
                    elif issubclass(type(v), object):
                        s = "..."
                    elif callable(v):
                        if hasattr(v, "__name__"):
                            s = v.__name__
                        else:
                            s = repr(v)
                    else:
                        s = repr(v)
                    if len(s) > 16:
                        s = s[0:13] + "..."
                    return s

                arg_values = (
                    f"{name}({' ' * (50 - len(name))}\n  "
                    + f",\n  ".join(
                        [
                            f"{key} = {r(parameters[key])}"
                            for key in parameter_names
                            if not key.startswith("_")
                        ]
                    )
                    + "\n)"
                )
                at = AnchoredText(
                    arg_values,
                    loc="upper left",
                    prop=dict(size=10, fontfamily="sans-serif"),
                    frameon=True,
                    bbox_to_anchor=(1.025, 0.75),
                    bbox_transform=ax.transAxes,
                )
                ax.add_artist(at)
                at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
                at.patch.set_facecolor("wheat")

    anim = FuncAnimation(fig.fig, func=one_frame, frames=gen, interval=interval)

    if show_params:
        fig.fig.tight_layout(pad=2, rect=[0, 0, 0.75, 1])
    else:
        fig.fig.tight_layout(pad=2)
    video = anim.to_jshtml(default_mode=default_mode)

    plots.close(fig.fig)
    display(HTML(video))

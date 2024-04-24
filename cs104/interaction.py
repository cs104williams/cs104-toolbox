"""
Objects for creating interactive visualizations.

The key function is `interact`, which is modeled after the underlying 
matplotlib function.  The `interact` function takes a function, and then
a list of keyword arges matching the parameter names for the function 
to Control objects, each of which describes how the user may adjust 
each parameter to the given function.
"""

__all__ = [
    "interact",
    "Fixed",
    "CheckBox",
    "Slider",
    "Choice",
    "record",
    "html_interact",
]

import json
import textwrap
from IPython.display import display
import ipywidgets
import numpy as np
import uuid
import itertools
import matplotlib.pyplot as plt
from datascience import Table
from abc import ABC, abstractmethod


from .docs import doc_tag
import inspect

counter = 0


def uuid():
    global counter
    counter += 1
    return f"i_{counter}"


class Control(ABC):
    def __init__(self):
        self._uid = uuid()

    def __str__(self):
        return str(self._v)

    @abstractmethod
    def _html(self, name):
        pass

    @abstractmethod
    def _script(self, name):
        pass

    @abstractmethod
    def _input_var(self, name):
        pass

    @abstractmethod
    def _values(self):
        pass


class Fixed(Control):
    """
    A paramater with a fixed value.
    """

    def __init__(self, value=None):
        super().__init__()
        self._value = value
        self._v = ipywidgets.interaction.fixed(value)

    def _html(self, name):
        return ""

    def _script(self):
        return f"""function {self._uid}_value() {{ return {self._value}; }}"""

    def _input_var(self):
        return None

    def _values(self):
        return [self._value]


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
        super().__init__()
        self._v = initial

    def _html(self, name):
        uid = self._uid
        return f"""\
            <div class="interact-inline">
                <label class="interact-label" style=""></label>
                <label class="widget-label-basic">
                    <input type="checkbox" id="checkbox_{uid}" {'checked' if self._v else ''}>
                    <span title="{name}">{name}</span>
                </label>
            </div>
            """

    def _script(self):
        uid = self._uid
        return f"""
                var _checkbox_{uid} = document.getElementById('checkbox_{uid}');
                function {uid}_value() {{ return _checkbox_{uid}.checked; }}
                """

    def _input_var(self):
        return f"_checkbox_{self._uid}"

    def _values(self):
        return [True, False]


class Slider(Control):
    """
    An adjustable numerical parameter.  This parameter is
    displayed as a slider.
    """

    @doc_tag("interact")
    def __init__(self, *args):
        """
        The initializer takes two or three parameters.  The first two
        are the lo and hi values for the range.  The optional third is
        the step size.

        Alternatively, pass in an array of two or three values with the
        same meaning as above.
        """
        super().__init__()
        if np.shape(args) == (1, 2) or np.shape(args) == (1, 3):
            args = args[0]
        if np.shape(args) != (2,) and np.shape(args) != (3,):
            raise ValueError(f"{args} is not a valid range for a Slider.")

        self._v = args

    def _html(self, name):
        uid = self._uid
        if len(self._v) == 2:
            params = f'min="{self._v[0]}" max="{self._v[1]}"'
        else:
            params = f'min="{self._v[0]}" max="{self._v[1]}" step="{self._v[2]}"'

        return f"""\
            <div class="interact-inline">
                <label class="interact-label">{name}</label>
                <div>
                    <input type="range" id="slider_{uid}" {params}>
                </div>
                <div class="interact-readout" id="sliderValue_{uid}"></div>
            </div>
        """

    def _script(self):
        uid = self._uid
        return f"""\
            var _slider_{uid} = document.getElementById('slider_{uid}');
            function {uid}_value() {{ return _slider_{uid}.value; }}

            var _sliderValue_{uid} = document.getElementById('sliderValue_{uid}');
            _sliderValue_{uid}.textContent = _slider_{uid}.value;

            _slider_{uid}.addEventListener("input", function() {{
                _sliderValue_{uid}.textContent = this.value;
            }})
        """

    def _input_var(self):
        return f"_slider_{self._uid}"

    def _values(self):
        start, stop, step = (
            self._v[0],
            self._v[1],
            (self._v[2] if len(self._v) == 3 else 1),
        )
        return np.arange(start, stop + step, step)


class Choice(Control):
    """
    A parameter with discrete (non-numeric) values.  This parameter is
    displayed as a popup menu.
    """

    @doc_tag("interact")
    def __init__(self, *args):
        """
        The initializer takes any number of values to use in the menu,
        or a single value containing and array of values to use.
        """
        super().__init__()
        if len(args) == 1 and np.shape(args[0]) != ():
            args = args[0]
        self._v = list(args)

    def _html(self, name):
        uid = self._uid
        options = "".join(
            [f'<option data-value="{v}" value="{v}">{v}</option>' for v in self._v]
        )
        return textwrap.dedent(
            f"""\
            <div class="interact-inline">
                <label class="interact-label" for="choice_{uid}">{name}</label>
                    <select id="choice_{uid}">
                        {options}
                    </select>
            </div>
            """
        )

    def _script(self):
        uid = self._uid
        return f"""
                var _choice_{uid} = document.getElementById('choice_{uid}');
                function {uid}_value() {{ return _choice_{uid}.value; }}
                """

    def _input_var(self):
        return f"_choice_{self._uid}"

    def _values(self):
        return self._v


def create_csv_line(values):
    def escape_and_quote(value):
        # Convert value to string just in case it's not
        str_value = str(value)
        if type(value) == bool:
            str_value = str_value.lower()

        # Escape double quotes by doubling them
        str_value = str_value.replace('"', '""')
        # Enclose in double quotes if the value contains a comma, newline, or double quote
        if "," in str_value or "\n" in str_value or '"' in str_value:
            str_value = f'"{str_value}"'
        return str_value

    # Apply the escape and quote function to each value and join with commas
    return ",".join(escape_and_quote(value) for value in values)


def _permutations(f, kwargs):

    def htmlify(v):
        if hasattr(v, "_repr_html_"):
            return v._repr_html_()    # yep, fancy format!
        else:
            return f"<pre>{v}</pre>"

    lists = [
        [(param, v) for v in control._values()] for param, control in kwargs.items()
    ]

    # Turn off plotting and make tables bigger while computing the function.
    # Add any other special cases about displaying output here.
    with plt.ioff():
        res = list(itertools.product(*lists))
        max_str_rows = Table.max_str_rows
        try:
            Table.max_str_rows = 30
            precomputed = [
                (create_csv_line((list(zip(*params))[1])), htmlify(f(**dict(params))))
                for params in res
            ]
        finally:
            Table.max_str_rows = max_str_rows

    return json.dumps(dict(precomputed), indent=2)


def check_parameters(f, kwargs):
    parameter_names = inspect.signature(f).parameters.keys()

    missing = [p for p in parameter_names if p not in kwargs]
    if missing != []:
        raise ValueError(
            f"Missing arguments to interact: {', '.join(missing)}.  You must provide an argument for each parameter of {f.__name__}."
        )

    for param, value in kwargs.items():
        if not issubclass(type(value), Control):
            raise ValueError(
                f"Parameter for {param} is not a control -- did you mean {param}=Fixed(...)?"
            )


def make_widgets(f, kwargs):
    check_parameters(f, kwargs)
    widgets = dict()

    for param, value in kwargs.items():
        widgets[param] = value._v

    return widgets


def html_interact(f, **kwargs):
    uid = uuid()
    check_parameters(f, kwargs)

    htmls = [value._html(param) for (param, value) in kwargs.items()]
    scripts = [value._script() for (_, value) in kwargs.items()]
    inputs = [value._input_var() for (_, value) in kwargs.items()]

    full_html = textwrap.dedent(
        f"""\
                <div>
                    {"  ".join(htmls)}
                    <div class="interact-output" id="output_{uid}"></div>
                </div>
        """
    )
    full_scripts = "\n".join(scripts)

    listeners = "\n".join(
        [
            f"{name}.oninput = function() {{ update_{uid}(); }}"
            for name in inputs
            if name
        ]
    )

    updater = textwrap.dedent(
        f"""\
        function createCSVLine(values) {{
            return values.map(value => {{
                let stringValue = value.toString();
                // Escape existing double quotes
                stringValue = stringValue.replace(/"/g, '""');
                // If the value contains a comma, newline or double quote, enclose it in double quotes
                if (stringValue.includes(',') || stringValue.includes('\\n') || stringValue.includes('"')) {{
                    stringValue = `"${{stringValue}}"`;
                }}
                return stringValue;
            }}).join(',');
        }}
                              
        var _output_{uid} = document.getElementById('output_{uid}');
        var _cache_{uid} = {_permutations(f, kwargs)};

        function update_{uid}() {{
            var text = createCSVLine([{", ".join([ f"{value._uid}_value()" for _, value in kwargs.items() ])}]);
            _output_{uid}.innerHTML = _cache_{uid}[text];
        }} 
        update_{uid}();

    """
    )

    return textwrap.dedent(
        f"""\
        <style>
        .interact-inline {{
            display: flex; /* Aligns children (label, slider, readout) in a row */
            align-items: center; /* Centers the items vertically */
            font-family: var(--jp-ui-font-family);
        }}

        .interact-label {{
            width: 120px;
            overflow: hidden; /* Prevents the text from spilling out */
            text-overflow: ellipsis; /* Adds ellipses if the text overflows */
            white-space: nowrap; /* Keeps the text on a single line */
            text-align: right;
            margin-right: 10px;            
        }}

        .interact-readout {{
            width: 100px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            padding-left: 20px;
        }}

        .interact-output {{
            margin-top: 10px;
            background-color: white important!;
        }}
        </style>

        {full_html}
        <script>
        {full_scripts}
        {updater}
        {listeners}
        </script>
    """
    )


@doc_tag("interact")
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
    out = ipywidgets.Textarea(
        f"def gen():\n    pass\n",
        layout=ipywidgets.Layout(width="100%", height="200px"),
    )
    interactor.children = (
        (ipywidgets.Text(value="", description="_caption"),)
        + interactor.children
        + (out,)
    )

    def changed(change):
        args = "; ".join([f"{c.description} = {repr(c.value)}" for c in controls])
        out.value = out.value.replace(
            "    pass\n", f"    {args}\n    yield locals()\n    pass\n"
        )

    for child in controls:
        child.observe(changed, names="value")

    changed(None)

    display(interactor)

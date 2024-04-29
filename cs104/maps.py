"""
Utilities to facilitate drawing choropleths for three kinds of 
geographic data: state-level, country-level, and Hopkins Forst plot-level.

The datascience package contains general plotting functions.  These
are designed to make it easier in 104 for specific use cases.
"""

__all__ = ["States", "Countries", "HopkinsForest"]

from datascience import *
import numpy as np
import pkg_resources


def check_table(t):
    """
    Make sure table t has strings and numbers in the first two columns.
    """
    if t.num_columns < 2:
        ValueError("Table must have atleast two columns")
    geo_col = t.column(0)
    if not np.issubdtype(geo_col.dtype, np.character):
        raise ValueError("The first column passed to map_table must contain strings")
    num_col = t.column(1)
    if not np.issubdtype(num_col.dtype, np.number):
        raise ValueError(
            "The second column passed to map_table must contain numeric values"
        )


class States(Map):

    _default_lat_lon = [48, -102]
    _default_zoom = 3

    def map_table(table, **kwargs):
        """
        Create a choropleth for states.  The table should contain the two letter state
        codes in the first column, and numeric values in the second.

        The kwargs can include:

        * bins: A description of how to bin the data, in the same form as the
            table's hist() method.
        * pallette: Any of the matplitlib color maps.
            (https://matplotlib.org/stable/tutorials/colors/colormaps.html)

        """
        states = States.read_geojson(
            pkg_resources.resource_filename(__name__, "data/us-states.json")
        )

        kws = {"nan_fill_color": "gray", "nan_fill_opacity": 0.2, "line_opacity": 0.3}

        kws.update(kwargs)

        kws.setdefault("legend_name", table.labels[1])
        t = Table().with_columns("geo", table.column(0), "values", table.column(1))
        return states.color(t, **kws)

    def _autozoom(self):
        """Calculate zoom and location."""
        attrs = {}

        attrs["location"] = self._default_lat_lon
        attrs["zoom_start"] = self._default_zoom
        return attrs


class Countries(Map):

    def map_table(table, **kwargs):
        """
        Create a choropleth for countries.  The table should contain the three-letter
        country codes in the first column and numeric values in the second.  See here
        for country codes: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3#Current_codes.
        The codes may be uppercase or lowercase.

        The kwargs can include:

        * bins: A description of how to bin the data, in the same form as the
            table's hist() method.
        * pallette: Any of the matplitlib color maps.
            (https://matplotlib.org/stable/tutorials/colors/colormaps.html)

        """

        countries = Countries.read_geojson(
            pkg_resources.resource_filename(__name__, "data/world-countries.json")
        )

        kws = {"nan_fill_color": "gray", "nan_fill_opacity": 0.2, "line_opacity": 0.3}

        kws.update(kwargs)

        check_table(table)

        kws.setdefault("legend_name", table.labels[1])

        t = Table().with_columns(
            "geo", table.apply(lambda x: x.upper(), 0), "values", table.column(1)
        )
        return countries.color(t, **kws)


class HopkinsForest(Map):

    _default_zoom = 15

    def map_table(table, **kwargs):
        """
        Create a choropleth for Hopkins Forest.  The table should contain the plot codes
        in the first column and numeric values in the second.  Plot codes have the form
        'p00-1' or 'p1339', based on the map present in lecture 1.

        The kwargs can include:

        * bins: A description of how to bin the data, in the same form as the
            table's hist() method.
        * pallette: Any of the matplitlib color maps.
            (https://matplotlib.org/stable/tutorials/colors/colormaps.html)

        """
        countries = HopkinsForest.read_geojson(
            pkg_resources.resource_filename(__name__, "data/hopkins-forest.json")
        )

        kws = {"nan_fill_color": "gray", "nan_fill_opacity": 0.2, "line_opacity": 0.3}

        kws.update(kwargs)
        kws.setdefault("legend_name", table.labels[1])

        t = Table().with_columns("geo", table.column(0), "values", table.column(1))
        return countries.color(t, **kws)

    def _autozoom(self):
        attrs = super()._autozoom()
        attrs["zoom_start"] += 2
        return attrs

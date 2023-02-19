
from datascience import *
import numpy as np
import pkg_resources

class States(Map):
    
    _default_lat_lon = [48, -102]
    _default_zoom = 3
    
    def map_table(table, **kwargs):
        states = States.read_geojson(pkg_resources.resource_filename(__name__, 'data/us-states.json'))
        
        kws = kwargs.copy()
        kws.setdefault('legend_name',table.labels[1])
        t = Table().with_columns("geo", table.column(0),
                                 "values", table.column(1))
        return states.color(t, **kws)

    def _autozoom(self):
        """Calculate zoom and location."""
        attrs = {}

        attrs['location'] = self._default_lat_lon
        attrs['zoom_start'] = self._default_zoom
        return attrs
        
class Countries:
    
    countries = Map.read_geojson(pkg_resources.resource_filename(__name__, 'data/world-countries.json'))
    
    def map_table(table, **kwargs):
        kws = kwargs.copy()
        kws.setdefault('legend_name',table.labels[1])

        t = Table().with_columns("geo", table.apply(lambda x: x.upper(), 0),
                                 "values", table.column(1))
        return Countries.countries.color(t, **kws)
        
        
        

# class Map(_FoliumWrapper, collections.abc.Mapping):
#     """A map from IDs to features. Keyword args are forwarded to folium."""

#     _mapper = folium.Map
#     _default_lat_lon = (37.872, -122.258)
#     _default_zoom = 12

#     def __init__(self, features=(), ids=(), width=960, height=500, **kwargs):
#         if isinstance(features, np.ndarray):
#             features = list(features)
#         if isinstance(features, collections.abc.Sequence):
#             if len(ids) == len(features):
#                 features = dict(zip(ids, features))
#             else:
#                 assert len(ids) == 0
#                 features = dict(enumerate(features))
#         elif isinstance(features, _MapFeature):
#             features = {0: features}
#         assert isinstance(features, dict), 'Map takes a list or dict of features'
#         tile_style = None
#         if "tiles" in kwargs:
#             tile_style = kwargs.pop("tiles")
#         self._features = features
#         self._attrs = {
#             'tiles': tile_style if tile_style else 'OpenStreetMap',
#             'max_zoom': 17,
#             'min_zoom': 10,
#         }
#         self._width = width
#         self._height = height
#         self._attrs.update(kwargs)
#         self._set_folium_map()

#     def copy(self):
#         """
#         Copies the current Map into a new one and returns it.
#         Note: This only copies rendering attributes. The underlying map is NOT deep-copied.
#         This is as a result of no functionality in Folium. Ref: https://github.com/python-visualization/folium/issues/1207
#         """

#         m = Map(features=self._features, width=self._width,
#                    height=self._height, **self._attrs)
#         m._folium_map = self._folium_map
#         return m

#     def __getitem__(self, id):
#         return self._features[id]

#     def __len__(self):
#         return len(self._features)

#     def __iter__(self):
#         return iter(self._features)

#     def _set_folium_map(self):
#         index_map = self._attrs.pop("index_map", None)
#         cluster_labels = self._attrs.pop("cluster_labels", None)
#         self._folium_map = self._create_map()
#         if self._attrs.get("clustered_marker", False):
#             def customize_marker_cluster(color, label):
#                 # Returns string for icon_create_function
#                 hexcolor = mpl.colors.to_hex(color)
#                 return f"""
#                     function(cluster) {{ 
#                         return L.divIcon({{ 
#                             html: `<div
#                               style='
#                                 opacity: 0.85; 
#                                 background-color: {hexcolor}; 
#                                 border: solid 2px rgba(66,135,245,1);
#                                 border-radius: 50%;
#                                 height: 40px;'
#                               onmouseover="document.getElementById('{hexcolor}').style.visibility='visible'"
#                               onmouseout="document.getElementById('{hexcolor}').style.visibility='hidden'">
#                               <div id="{hexcolor}" 
#                                 style='
#                                   visibility: hidden;
#                                   font-size: 12px; 
#                                   background-color: white; 
#                                   color: {hexcolor};
#                                   text-align: center; 
#                                   padding: 6% 6%;
#                                   position: absolute; 
#                                   z-index: 1;
#                                   top: 120%; 
#                                   left: 50%; 
#                                   margin-left: -20px;
#                                   '>{label}</div>
#                             </div>`, 
#                             iconSize: [40, 40],
#                             className: 'dummy'
#                         }});
#                     }}
#                 """
#             if index_map is not None:
#                 chart_colors = (
#                     (0.0, 30/256, 66/256),
#                     (1.0, 200/256, 44/256),
#                     (0.0, 150/256, 207/256),
#                     (30/256, 100/256, 0.0),
#                     (172/256, 60/256, 72/256),
#                 )
#                 chart_colors += tuple(tuple((x+0.7)/2 for x in c) for c in chart_colors)
#                 colors = list(itertools.islice(itertools.cycle(chart_colors), len(cluster_labels)))
#                 marker_cluster = [MarkerCluster(icon_create_function = customize_marker_cluster(colors[i], label)).add_to(self._folium_map) for i, label in enumerate(cluster_labels)]
#             else:
#                 marker_cluster = MarkerCluster().add_to(self._folium_map)
#             clustered = True
#         else:
#             clustered = False
#         for i, feature in enumerate(self._features.values()):
#             if isinstance(feature, Circle):
#                 feature.draw_on(self._folium_map, self._attrs.get("radius_in_meters", False))
#             elif clustered and isinstance(feature, Marker):
#                 if isinstance(marker_cluster, list):
#                     feature.draw_on(marker_cluster[index_map[i]])
#                 else:
#                     feature.draw_on(marker_cluster)
#             else:
#                 feature.draw_on(self._folium_map)
#         if self._attrs.get("colorbar_scale", None) is not None:
#             colorbar_scale = self._attrs["colorbar_scale"]
#             include_color_scale_outliers = self._attrs.get("include_color_scale_outliers", False)
#             scale_colors = ["#340597", "#7008a5", "#a32494", "#cf5073", "#ee7c4c", "#f69344", "#fcc22d", "#f4e82d", "#f4e82d"]
#             vmin = colorbar_scale.pop(0)
#             vmax = colorbar_scale.pop(-1)
#             colormap = cm.LinearColormap(colors = scale_colors, index = colorbar_scale, caption = "*Legend above may exclude outliers." if not include_color_scale_outliers else "", vmin = colorbar_scale[0], vmax = colorbar_scale[-1])
#             self._folium_map.add_child(colormap)

#     def _create_map(self):
#         attrs = {'width': self._width, 'height': self._height}
#         attrs.update(self._autozoom())
#         attrs.update(self._attrs.copy())

#         # Enforce zoom consistency
#         attrs['max_zoom'] = max(attrs['zoom_start']+2, attrs['max_zoom'])
#         attrs['min_zoom'] = min(attrs['zoom_start']-2, attrs['min_zoom'])
#         return self._mapper(**attrs)

#     def _autozoom(self):
#         """Calculate zoom and location."""
#         bounds = self._autobounds()
#         attrs = {}

#         midpoint = lambda a, b: (a + b)/2
#         attrs['location'] = (
#             midpoint(bounds['min_lat'], bounds['max_lat']),
#             midpoint(bounds['min_lon'], bounds['max_lon'])
#         )

#         # remove the following with new Folium release
#         # rough approximation, assuming max_zoom is 18
#         import math
#         try:
#             lat_diff = bounds['max_lat'] - bounds['min_lat']
#             lon_diff = bounds['max_lon'] - bounds['min_lon']
#             area, max_area = lat_diff*lon_diff, 180*360
#             if area:
#                 factor = 1 + max(0, 1 - self._width/1000)/2 + max(0, 1-area**0.5)/2
#                 zoom = math.log(area/max_area)/-factor
#             else:
#                 zoom = self._default_zoom
#             zoom = max(1, min(18, round(zoom)))
#             attrs['zoom_start'] = zoom
#         except ValueError as e:
#             raise Exception('Check that your locations are lat-lon pairs', e)

#         return attrs

#     def _autobounds(self):
#         """Simple calculation for bounds."""
#         bounds = {}

#         def check(prop, compare, extreme, val):
#             opp = min if compare is max else max
#             bounds.setdefault(prop, val)
#             bounds[prop] = opp(compare(bounds[prop], val), extreme)

#         def bound_check(lat_lon):
#             lat, lon = lat_lon
#             check('max_lat', max, 90, lat)
#             check('min_lat', min, -90, lat)
#             check('max_lon', max, 180, lon)
#             check('min_lon', min, -180, lon)

#         lat_lons = [lat_lon for feature in self._features.values() for
#                     lat_lon in feature.lat_lons]
#         if not lat_lons:
#             lat_lons.append(self._default_lat_lon)
            
#         for lat_lon in lat_lons:
#              bound_check(lat_lon)

#         return bounds

#     @property
#     def features(self):
#         feature_list = []
#         for key, value in self._features.items():
#             f = collections.OrderedDict([('id', key), ('feature', value)])
#             f.update(value.properties)
#             feature_list.append(f)
#         return feature_list

#     def format(self, **kwargs):
#         """Apply formatting."""
#         attrs = self._attrs.copy()
#         attrs.update({'width': self._width, 'height': self._height})
#         attrs.update(kwargs)
#         return Map(self._features, **attrs)

#     def geojson(self):
#         """Render features as a FeatureCollection."""
#         return {
#             "type": "FeatureCollection",
#             "features": [f.geojson(i) for i, f in self._features.items()]
#         }

#     def color(self, values, ids=(), key_on='feature.id', palette='YlOrBr', **kwargs):
#         """Color map features by binning values.

#         values -- a sequence of values or a table of keys and values
#         ids -- an ID for each value; if none are provided, indices are used
#         key_on -- attribute of each feature to match to ids
#         palette -- one of the following color brewer palettes:

#             'BuGn', 'BuPu', 'GnBu', 'OrRd', 'PuBu', 'PuBuGn', 'PuRd', 'RdPu',
#             'YlGn', 'YlGnBu', 'YlOrBr', and 'YlOrRd'.

#         Defaults from Folium:

#         threshold_scale: list, default None
#             Data range for D3 threshold scale. Defaults to the following range
#             of quantiles: [0, 0.5, 0.75, 0.85, 0.9], rounded to the nearest
#             order-of-magnitude integer. Ex: 270 rounds to 200, 5600 to 6000.
#         fill_opacity: float, default 0.6
#             Area fill opacity, range 0-1.
#         line_color: string, default 'black'
#             GeoJSON geopath line color.
#         line_weight: int, default 1
#             GeoJSON geopath line weight.
#         line_opacity: float, default 1
#             GeoJSON geopath line opacity, range 0-1.
#         legend_name: string, default None
#             Title for data legend. If not passed, defaults to columns[1].
#         """
#         # Set values and ids to both be simple sequences by inspecting values
#         id_name, value_name = 'IDs', 'values'
#         if isinstance(values, collections.abc.Mapping):
#             assert not ids, 'IDs and a map cannot both be used together'
#             if hasattr(values, 'columns') and len(values.columns) == 2:
#                 table = values
#                 ids, values = table.columns
#                 id_name, value_name = table.labels
#             else:
#                 dictionary = values
#                 ids, values = list(dictionary.keys()), list(dictionary.values())
#         if len(ids) != len(values):
#             assert len(ids) == 0
#             # Use indices as IDs
#             ids = list(range(len(values)))

#         m = self._create_map()
#         data = pandas.DataFrame({id_name: ids, value_name: values})
#         attrs = {
#             'geo_data': json.dumps(self.geojson()),
#             'data': data,
#             'columns': [id_name, value_name],
#             'key_on': key_on,
#             'fill_color': palette,
#         }
#         kwargs.update(attrs)
#         folium.Choropleth(
#             **kwargs,
#             name='geojson'
#         ).add_to(m)
#         colored = self.format()
#         colored._folium_map = m
#         return colored

#     def overlay(self, feature, color='Blue', opacity=0.6):
#         """
#         Overlays ``feature`` on the map. Returns a new Map.

#         Args:
#             ``feature``: a ``Table`` of map features, a list of map features,
#                 a Map, a Region, or a circle marker map table. The features will
#                 be overlayed on the Map with specified ``color``.

#             ``color`` (``str``): Color of feature. Defaults to 'Blue'

#             ``opacity`` (``float``): Opacity of overlain feature. Defaults to
#                 0.6.

#         Returns:
#             A new ``Map`` with the overlain ``feature``.
#         """
#         result = self.copy()
#         if type(feature) == Table:
#             # if table of features e.g. Table.from_records(taz_map.features)
#             if 'feature' in feature.labels:
#                 feature = feature['feature']

#             # if marker table e.g. table with columns: latitudes,longitudes,popup,color,area
#             else:
#                 feature = Circle.map_table(feature)

#         if type(feature) in [list, np.ndarray]:
#             for f in feature:
#                 f._attrs['fill_color'] = color
#                 f._attrs['fill_opacity'] = opacity
#                 f.draw_on(result._folium_map)

#         elif type(feature) == Map:
#             for i in range(len(feature._features)):
#                 f = feature._features[i]
#                 f._attrs['fill_color'] = color
#                 f._attrs['fill_opacity'] = opacity
#                 f.draw_on(result._folium_map)
#         elif type(feature) == Region:
#             feature._attrs['fill_color'] = color
#             feature._attrs['fill_opacity'] = opacity
#             feature.draw_on(result._folium_map)
#         return result

#     @classmethod
#     def read_geojson(cls, path_or_json_or_string_or_url):
#         """Read a geoJSON string, object, file, or URL. Return a dict of features keyed by ID."""
#         assert path_or_json_or_string_or_url
#         data = None
#         if isinstance(path_or_json_or_string_or_url, (dict, list)):
#             data = path_or_json_or_string_or_url
#         try:
#             data = json.loads(path_or_json_or_string_or_url)
#         except ValueError:
#             pass
#         try:
#             path = path_or_json_or_string_or_url
#             if path.endswith('.gz') or path.endswith('.gzip'):
#                 import gzip
#                 contents = gzip.open(path, 'r').read().decode('utf-8')
#             else:
#                 contents = open(path, 'r').read()
#             data = json.loads(contents)
#         except FileNotFoundError:
#             pass
#         if not data:
#             import urllib.request
#             with urllib.request.urlopen(path_or_json_or_string_or_url) as url:
#                 data = json.loads(url.read().decode())
#         assert data, 'MapData accepts a valid geoJSON object, geoJSON string, path to a geoJSON file, or URL'
#         return cls(cls._read_geojson_features(data))

#     @staticmethod
#     def _read_geojson_features(data, features=None, prefix=""):
#         """Return a dict of features keyed by ID."""
#         if features is None:
#             features = collections.OrderedDict()
#         for i, feature in enumerate(data['features']):
#             key = feature.get('id', prefix + str(i))
#             feature_type = feature['geometry']['type']
#             if feature_type == 'FeatureCollection':
#                 _read_geojson_features(feature, features, prefix + '.' + key)
#             elif feature_type == 'Point':
#                 value = Circle._convert_point(feature)
#             elif feature_type in ['Polygon', 'MultiPolygon']:
#                 value = Region(feature)
#             else:
#                 # TODO Support all http://geojson.org/geojson-spec.html#geometry-objects
#                 value = None
#             features[key] = value
#         return features

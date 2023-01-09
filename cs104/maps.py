
from datascience import *
import numpy as np
import pkg_resources

class States:
    
    states = Map.read_geojson(pkg_resources.resource_filename(__name__, 'data/us-states.json'))
    
    def map_table(table, **kwargs):
        t = Table().with_columns("geo", table.column(0),
                                 "values", table.column(1))
        return States.states.color(t, legend_name=table.labels[1])
        
        
class Countries:
    
    countries = Map.read_geojson(pkg_resources.resource_filename(__name__, 'data/world-countries.json'))
    
    def map_table(table, **kwargs):
        t = Table().with_columns("geo", table.apply(lambda x: x.upper(), 0),
                                 "values", table.column(1))
        return Countries.countries.color(t, legend_name=table.labels[1])
        
        
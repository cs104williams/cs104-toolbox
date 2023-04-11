"""
"""

__all__ = [ 'cleaned', 'with_cleaned_columns']

from datascience import *
import numpy as np
import matplotlib.pyplot as plots
import matplotlib.colors as colors

import collections
import collections.abc


def has_type(T):
    """Return a function that indicates whether value can be converted
       to the type T."""
    def is_a_T(v):
        try:
            T(v)
            return True
        except ValueError:
            return False
    return is_a_T

def clean_for_column(table, column_name, expected_type):
    """Given a table, and column name, and the type of data you expect
       in that column (eg: str, int, or float), this function returns
       a new copy of the table with the following changes:
    
         - Any rows with missing values in the given column are removed.
         - Any rows with values in the given column that are not of the 
           expected type are removed.

        Returns a new table and also a table with the removed rows
    """
    
    # Remove rows w/ nans.  Columns with floats are treated different, since nans are 
    #  converted in np.nan when a floating point column is created in read_table.
    if (table.column(column_name).dtype == np.float64):
        new_table = table.where(column_name, lambda x: not np.isnan(x))
        removed_rows = table.where(column_name, lambda x: np.isnan(x))
    else:
        new_table = table.where(column_name, are.not_equal_to('nan'))
        removed_rows = table.where(column_name, are.equal_to('nan'))

    # Remove rows w/ values that cannot be converted to the expected type.
    removed_rows.append(new_table.where(column_name, lambda x: not has_type(expected_type)(x)))
    new_table = new_table.where(column_name, has_type(expected_type))

    # Make sure all rows have values of the expected type.  (eg: convert str's to int's for an
    #   int column.)
    new_table = new_table.with_column(column_name, new_table.apply(expected_type, column_name))
    
    return new_table, removed_rows

def clean_for_columns(table, *labels_and_types):
    
    if len(labels_and_types) == 1:
        labels_and_types = labels_and_types[0]
    if isinstance(labels_and_types, collections.abc.Mapping):
        labels_and_types = list(labels_and_types.items())
    if not isinstance(labels_and_types, collections.abc.Sequence):
        labels_and_types = list(labels_and_types)
    if not labels_and_types:
        return table
    first = labels_and_types[0]
    
    if not isinstance(first, str) and hasattr(first, '__iter__'):
        for pair in labels_and_types:
            if len(pair) != 2:
                raise ValueError('incorrect columns format -- should be a list alternating labels and types')
        labels_and_types = [x for pair in labels_and_types for x in pair]
        
    if len(labels_and_types) % 2 != 0:
        raise ValueError('incorrect columns format -- should be a list alternating labels and types')
        
    kept = table.copy()
    removed = Table(kept.labels)
    for i in range(0, len(labels_and_types), 2):
        label, expected_type = labels_and_types[i], labels_and_types[i+1]
        kept, dropped = clean_for_column(kept, label, expected_type)
        removed.append(dropped)
    
    return (kept, removed)
            

def take_clean(table, *labels_and_types):
    clean, dirty = clean_for_columns(table, *labels_and_types)
    return clean

def take_dirty(table, *labels_and_types):
    clean, dirty = clean_for_columns(table, *labels_and_types)
    return dirty


def cleaned(table, *expected_types):
    """
    """
    labels = table.labels
    
    if len(expected_types) == 1:
        expected_types = expected_types[0]
    
    if len(labels) != len(expected_types):
        raise ValueError("table has {} columns but {} types provided."
                            .format(len(labels), len(expected_types)))
        
    return with_clean_columns(table, list(zip(labels, expected_types)))

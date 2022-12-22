"""Utility functions"""

__all__ = ['test', 'test_equal', 'test_close', 'test_not_equal']

import traceback
import numpy as np

def _print_message(test, message):
    print("\u001b[35;1m")
    print("---------------------------------------------------------------------------")
    print("Yipes! " + test)
    print()
    for line in str(message).strip().split("\n"):
        print("  ", line)
    print("\u001b[0m")

def test(a):
    if not a:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, "Expression is not True.")
        
def test_equal(a,b):
    try:
        np.testing.assert_equal(a,b)
    except AssertionError as e:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, e)

def test_close(a,b,atol=1e-5):
    try:
        np.testing.assert_allclose(a,b,atol=atol)
    except AssertionError as e:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, e)

def test_not_equal(a,b):
    try:
        np.testing.a
    except AssertionError as e:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, e)

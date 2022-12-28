"""Utility functions"""

# __all__ = ['test_is_true', 'test_equal', 'test_close']

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

def test_is_true(a):
    if not a:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, "Expression is not True")
        
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
        
def test_in(a, *r):
    if len(r) == 1:
        r = r[0]
        
    if a not in r:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, f"{a} is not in range {r}")

def test_between(a, *interval):

    if len(interval) == 1:
        interval = interval[0]
        
    if np.shape(interval) != (2,):
        raise ValueError("Interval must be passed as two numbers or an array containing two numbers")
        
    if a < interval[0] or a >= interval[1]:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, f"{a} is not in interval [{interval[0]}, {interval[1]})")

def test_between_or_equal(a, *interval):

    if len(interval) == 1:
        interval = interval[0]
        
    if np.shape(interval) != (2,):
        raise ValueError("Interval must be passed as two numbers or an array containing two numbers")
        
    if a < interval[0] or a > interval[1]:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, f"{a} is not in interval [{interval[0]}, {interval[1]}]")

def test_strictly_between(a, *interval):

    if len(interval) == 1:
        interval = interval[0]
        
    if np.shape(interval) != (2,):
        raise ValueError("Interval must be passed as two numbers or an array containing two numbers")
        
    if a <= interval[0] or a >= interval[1]:
        tbo = traceback.extract_stack()
        _print_message(tbo[-2].line, f"{a} is not in interval ({interval[0]}, {interval[1]})")

def test_less_than(*a):
    for i in range(len(a)-1):
        if not np.all(np.less(a[i], a[i+1])):
            tbo = traceback.extract_stack()
            _print_message(tbo[-2].line, f"Expression is not true: " + " < ".join([str(x) for x in a]))
            return

def test_less_than_or_equal(*a):
    for i in range(len(a)-1):
        if not np.all(np.less_equal(a[i], a[i+1])):
            tbo = traceback.extract_stack()
            _print_message(tbo[-2].line, f"Expression is not true: " + " <= ".join([str(x) for x in a]))
            return

# __all__ = ['test_is_true', 'test_equal', 'test_close']

import traceback
import numpy as np
from IPython.core.magic import register_cell_magic, needs_local_scope
import sys

_message_count = 0

def _print_message(test, message):
    global _message_count
    _message_count += 1
    print("\u001b[35;1m")
    print("---------------------------------------------------------------------------")
    print("Yipes! " + test)
    print()
    for line in str(message).strip().split("\n"):
        print("  ", line)
    print("\u001b[0m")

def _extact_test_as_text():
    # The frame with the test call is the third from the top if we call 
    # a test function directly
    tbo = traceback.extract_stack()
    text = tbo[-3].line
    
    # If we use the magic cells, then that frame will have an empty line,
    # and we must look back to the fourth frame from the top to get the code
    # from the local variable in the `test` function below.
    if text == '':
        local_vars = sys._getframe().f_back.f_back.f_back.f_locals
        line = local_vars.get('line', '?')
        text = line + ": " + local_vars.get('text_as_text', "<can't find test text>")
        
    return text

def test_is_true(a):
    if not a:
        _print_message(_extact_test_as_text(), "Expression is not True")
        
def test_equal(a,b):
    try:
        np.testing.assert_equal(a,b)
    except AssertionError as e:
        _print_message(_extact_test_as_text(), e)

def test_close(a,b,atol=1e-5):
    try:
        np.testing.assert_allclose(a,b,atol=atol)
    except AssertionError as e:
        _print_message(_extact_test_as_text(), e)
        
def test_in(a, *r):
    if len(r) == 1:
        r = r[0]
    if a not in r:
        _print_message(_extact_test_as_text(), f"{a} is not in range {r}")

def _grab_interval(*interval):
    if len(interval) == 1:
        interval = interval[0]
    if np.shape(interval) != (2,):
        raise ValueError(f"Interval must be passed as two numbers or an array containing two numbers, not {interval}")            
    return interval
        
def test_between(a, *interval):
    interval = _grab_interval(*interval)
    if a < interval[0] or a >= interval[1]:
        _print_message(_extact_test_as_text(), f"{a} is not in interval [{interval[0]}, {interval[1]})")

def test_between_or_equal(a, *interval):
    interval = _grab_interval(*interval)
    if a < interval[0] or a > interval[1]:
        _print_message(_extact_test_as_text(), f"{a} is not in interval [{interval[0]}, {interval[1]}]")

def test_strictly_between(a, *interval):
    interval = _grab_interval(*interval)
    if a <= interval[0] or a >= interval[1]:
        _print_message(_extact_test_as_text(), f"{a} is not in interval ({interval[0]}, {interval[1]})")

def test_less_than(*a):
    for i in range(len(a)-1):
        if not np.all(np.less(a[i], a[i+1])):
            _print_message(_extact_test_as_text(), f"Expression is not true: " + " < ".join([str(x) for x in a]))
            return

def test_less_than_or_equal(*a):
    for i in range(len(a)-1):
        if not np.all(np.less_equal(a[i], a[i+1])):
            _print_message(_extact_test_as_text(), f"Expression is not true: " + " <= ".join([str(x) for x in a]))
            return

    
@register_cell_magic
@needs_local_scope
def test(line, cell, local_ns=None): 
    original_count = _message_count
    for text_as_text in cell.split("\n"):
        if text_as_text != '':
            try:
                eval(text_as_text, local_ns)
            except Exception as e:
                etype, evalue, tb = sys.exc_info()
                
                # Take all the frames above the one for the call to eval, which
                # will have the file name <string>.
                files = [ frame.filename for frame in traceback.extract_tb(tb) ]
                index = files.index('<string>')
                limit = index - len(files) + 1
                tbo = traceback.format_exception(etype, evalue, tb, limit=limit)
                
                _print_message(line + ": " + text_as_text, "\n".join(tbo))

    if original_count == _message_count:
        if line.strip() != '':
            print("\u001b[35;1mPassed all tests for " + line + "!\u001b[0m")
        else:
            print("\u001b[35;1mPassed all tests!\u001b[0m")
                
    return None
# __all__ = ['test_is_true', 'test_equal', 'test_close']

import traceback
import numpy as np
# from IPython.core.magic import register_cell_magic, needs_local_scope
# import sys
import ast


def _in_otter():
    for frame in traceback.StackSummary.extract(traceback.walk_stack(None)):
        if frame.filename.endswith('ok_test.py'):
            return True
    return False


def _print_message(test, message):
    # if in otter, skip the header and the ANSI color codes because Otter 
    #   already shows all the info in its HTML-formatted error messages.
    in_otter = _in_otter()
    
    if not in_otter: 
        print("\u001b[35;1m")
        print("---------------------------------------------------------------------------")
        print("Yipes! " + test)
        print("                                                                           ")
        
    for line in str(message).strip().split("\n"):
        print("  ", line)
        
    if not in_otter: 
        print("\u001b[0m")

def _arguments(test_line):
    test_line = test_line.strip()
    tree = ast.parse(test_line, mode='eval')
    args = [ test_line[x.col_offset:x.end_col_offset].strip() for x in tree.body.args]
    return args
    
    
def _extact_test_as_text():
    # The frame with the test call is the third from the top if we call 
    # a test function directly
    tbo = traceback.extract_stack()
    text = tbo[-3].line
    
    # # If we use the magic cells, then that frame will have an empty line,
    # # and we must look back to the fourth frame from the top to get the code
    # # from the local variable in the `test` function below.
    # if text == '':
    #     local_vars = sys._getframe().f_back.f_back.f_back.f_locals
    #     line = local_vars.get('line', '?')
    #     text = line + ": " + local_vars.get('text_as_text', 
    #                                         "<can't find test text>")
        
    return text

def check(a):
    if not a:
        _print_message(_extact_test_as_text(), "Expression is not True")
        
def check_equal(a,b):
    try:
        np.testing.assert_equal(a,b)
    except AssertionError as e:
        _print_message(_extact_test_as_text(), f"{a} is not equal to {b}")

def check_close(a,b,atol=1e-5):
    try:
        np.testing.assert_allclose(a,b,atol=atol)
    except AssertionError as e:
        _print_message(_extact_test_as_text(), f"{a} is not between {b-atol} and {b+atol}")

def _shorten(x):
    return np.array2string(np.array(x),threshold=10)
    # if np.shape(x) != () and len(x) > 10:
    #     return "[" + " ".join([str(v) for v in x[:5]] + [ "..." ] + [str(v) for v in x[-5:]]) + "]"
    # else:
    #     return str(x)
        
def check_in(a, *r):
    if len(r) == 1:
        r = r[0]
    if a not in r:
        _print_message(_extact_test_as_text(), f"{a} is not in range {_shorten(r)}")

def _grab_interval(*interval):
    if len(interval) == 1:
        interval = interval[0]
    if np.shape(interval) != (2,):
        raise ValueError(f"Interval must be passed as two numbers " +
                         "or an array containing two numbers, not {interval}")            
    return interval
        
def check_between(a, *interval):
    interval = _grab_interval(*interval)
    if a < interval[0] or a >= interval[1]:
        _print_message(_extact_test_as_text(), 
                       f"{a} is not in interval [{interval[0]}, {interval[1]})")

def check_between_or_equal(a, *interval):
    interval = _grab_interval(*interval)
    if a < interval[0] or a > interval[1]:
        _print_message(_extact_test_as_text(), 
                       f"{a} is not in interval [{interval[0]}, {interval[1]}]")

def check_strictly_between(a, *interval):
    interval = _grab_interval(*interval)
    if a <= interval[0] or a >= interval[1]:
        _print_message(_extact_test_as_text(), 
                       f"{a} is not in interval ({interval[0]}, {interval[1]})")

# def _value_at_index_if_array(v, i):
#     if np.shape(v) == ():
#         return v
#     else:
#         return v.item(i)
        
# def _binary_less_than(source_terms, values):
#     result = np.less(values[0], values[1])
#     if np.all(result):
#         return None
#     else:
#         shape = np.shape(result)
#         print(shape)
#         if shape == ():
#             return f"check_less_than({source_terms[0]}, {source_terms[1]}) failed:\n" + \
#                    f"    Expression is not true: " + " < ".join([_shorten(x) for x in values])
#         elif len(shape) == 1:
#             false_indices = np.where(result == False)
#             return f"check_less_than({source_terms[0]}, {source_terms[1]}) failed:\n" + \
#                    f"    Expression is not true at indices {_shorten(false_indices[0])}"
#         else:
#             return f"Expression is not true: " + " < ".join([_shorten(x) for x in values])

# def check_less_than(*a):
#     text = _extact_test_as_text()
#     args = _arguments(text)
#     for i in range(len(a)-1):
#         result = _binary_less_than(args[i:i+2], a[i:i+2])
#         if result != None:
#             _print_message(_extact_test_as_text(), result)
#             return
        
            
        
def check_less_than(*a):
    for i in range(len(a)-1):
        result = np.less(a[i], a[i+1])
        if not np.all(result):
            text = _extact_test_as_text()
            args = _arguments(text)
            _print_message(_extact_test_as_text(), 
                           f"Expression is not true: " + " < ".join([_shorten(x) for x in args[i:i+2]]))
            return

# def check_less_than(*a):
#     for i in range(len(a)-1):
#         result = np.less(a[i], a[i+1])
#         if not np.all(result):
#             text = _extact_test_as_text()
#             args = _arguments(text)
#             _print_message(_extact_test_as_text(), 
#                            f"Expression is not true: " + " < ".join([_shorten(x) for x in args[i:i+2]]))
#             return
        
        
def check_less_than_or_equal(*a):
    for i in range(len(a)-1):
        if not np.all(np.less_equal(a[i], a[i+1])):
            text = _extact_test_as_text()
            args = _arguments(text)
            _print_message(_extact_test_as_text(), 
                           f"Expression is not true: " + " <= ".join([_shorten(x) for x in args[i:i+2]]))
            return

    
# @register_cell_magic
# @needs_local_scope
# def test(line, cell, local_ns=None): 
#     original_count = _message_count
#     for text_as_text in cell.split("\n"):
#         if text_as_text != '':
#             try:
#                 eval(text_as_text, local_ns)
#             except Exception as e:
#                 etype, evalue, tb = sys.exc_info()
                
#                 # Take all the frames above the one for the call to eval, which
#                 # will have the file name <string>.
#                 files = [ frame.filename for frame in traceback.extract_tb(tb) ]
#                 index = files.index('<string>')
#                 limit = index - len(files) + 1
#                 tbo = traceback.format_exception(etype, evalue, tb, limit=limit)
                
#                 _print_message(line + ": " + text_as_text, "\n".join(tbo))

#     if original_count == _message_count:
#         if line.strip() != '':
#             print("\u001b[35;1mPassed all tests for " + line + "!\u001b[0m")
#         else:
#             print("\u001b[35;1mPassed all tests!\u001b[0m")
                
#     return None
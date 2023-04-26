p__all__ = ['check', 
           'check_equal',
           'check_close',
           'check_less_than',
           'check_less_than_or_equal',
           'check_between',
           'check_in',
           'check_type',
           'check_not', 
           'check_not_equal',
           'check_not_close',
           'check_not_less_than',
           'check_not_less_than_or_equal',
           'check_not_between',
           'check_not_in',
           'check_not_type'           
          ]

import traceback
import numpy as np
import ast
from textwrap import indent

from .docs import doc_tag

def in_otter():
    for frame in traceback.StackSummary.extract(traceback.walk_stack(None)):
        if frame.filename.endswith('ok_test.py'):
            return True
    return False

def print_message(test, message):
    if np.shape(message) != ():
        message = "\n".join(message)

    # if in otter, skip the header and the ANSI color codes because Otter 
    #   already shows all the info in its HTML-formatted error messages.
    in_jupyter = not in_otter()
    
    if in_jupyter:
        print("\u001b[35m\u001b[1m🐝 " + test)      
        print(indent(message, "      "))
        print("\u001b[0m")
    else:
        print(indent(message.strip(), "      "))

def arguments_from_check_call(test_line):
    test_line = test_line.strip()
    tree = ast.parse(test_line, mode='eval')
    args = [ test_line[x.col_offset:x.end_col_offset].strip() for x in tree.body.args]
    return args
    
    
def source_for_check_call():
    # The frame with the test call is the third from the top if we call 
    # a test function directly
    # Actually fourth with the doc tags...
    tbo = traceback.extract_stack()
    return tbo[-4].line

def pvalue(x):
    """Print a value in a readable way, either via repr or via an abbreviated np-array."""
    if np.shape(x) == ():
        return repr(x)
    else:
        return np.array2string(np.array(x),threshold=10)

def short_form_for_value(x):
    # x may be a list or array, so make sure an array...
    return np.array2string(np.array(x),threshold=10)

def term_and_value(arg, value):
    if arg == repr(value):
        return None, value
    else:
        return f"{arg} == {pvalue(value)}", value

def term_and_value_at_index(arg, value, index):
    if arg == repr(value):
        return None, value
    elif np.shape(value) == ():
        return f"{arg} == {pvalue(value)}", value
    else:
        value = np.array(value)
        return f"{arg}.item({index}) == {pvalue(value.item(index))}", value.item(index)

def arrayify(x):
    if np.shape(x) == ():
        return x
    else:
        return np.array(x)
    
def binary_check(args_source, args_values, test_op, test_str):
    result = test_op(*args_values)
    if not np.all(result):
        shape = np.shape(result)
        if shape == ():
            terms,values = tuple(zip(*[ term_and_value(*x) for x in zip(args_source,args_values) ]))
            arg_terms = "".join([ x + " and " for x in terms if x != None])
            return [ f"{arg_terms}{test_str(*values)}" ]
        elif len(shape) == 1:
            message = [  ]
            false_indices = np.where(result == False)[0]
            for i in false_indices[0:3]:
                terms,values = tuple(zip(*[ term_and_value_at_index(*x,i) for x in zip(args_source,args_values) ]))
                arg_terms = "".join([ x + " and " for x in terms if x != None])
                message += [ f"{arg_terms}{test_str(*values)}" ]
            if len(false_indices) > 3:
                message += [ f"... omitting {len(false_indices)-3} more case(s)" ]
            return message 
        else:
            return [ f"{test_str(*map(short_form_for_value, args_values))}" ]
    else:
        return []
    

def grab_interval(*interval):
    if len(interval) == 1:
        interval = interval[0]
    if np.shape(interval) != (2,) or np.shape(interval[0]) != () or np.shape(interval[1]) != ():
        raise ValueError()            
    return arrayify(interval)
            
def interval_check(args_source, a, interval, test_op):
    try:
        interval = grab_interval(*interval)
    except ValueError as err:
        return [ f"Interval must be passed as two numbers " +
                 f"or an array containing two numbers, not {interval}" ]
    
    result = test_op(a, interval)
    
    if not np.all(result):
        shape = np.shape(result)
        if len(shape) == 1:
            message = [ ]
            false_indices = np.where(result == False)[0]
            for i in false_indices[0:3]:
                ai,av = term_and_value_at_index(args_source[0],a,i)
                if ai != None:
                    terms = ai + " and "
                else:
                    terms = ""
                message += [ f"{terms}{pvalue(av)} is not in interval [{interval[0]},{interval[1]})" ]
            if len(false_indices) > 3:
                message += [ f"... omitting {len(false_indices)-3} more case(s)" ]
        else:
            message = [ f"{pvalue(a)} is not in interval [{interval[0]},{interval[1]})" ]
        return message
    else:
        return []


    
def ordering_check(args, a, compare_fn, message_fn):
    message = []
    for i in range(len(a)-1):
        m = binary_check(args[i:i+2], a[i:i+2], compare_fn, message_fn)            
        if len(m) > 0 and len(message) > 0:
            message += [ "" ]
        message += m
    return message


### Entry points

@doc_tag()
def check(a):
    a = arrayify(a)
    
    if not np.all(a):
        print_message(source_for_check_call(), "Expression is not True")
                
@doc_tag()
def check_equal(a, b):
    a,b = arrayify(a),arrayify(b)
    
    try:
        text = source_for_check_call()
        args = arguments_from_check_call(text)   
        message = binary_check(args, [a, b], 
                               lambda x,y: x == y, 
                               lambda x,y: f"{pvalue(x)} != {pvalue(y)}")       
    except e:
        message = [ str(e) ]
        
    if message != []:
        print_message(text, message)
    
@doc_tag()
def check_close(a, b, plus_or_minus=1e-5):
    a,b = arrayify(a),arrayify(b)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)        
    message = binary_check(args, [a, b], 
                           lambda x,y: np.isclose(x,y,atol=plus_or_minus), 
                           lambda x,y: f"{x} < {y-plus_or_minus} or {y+plus_or_minus} < {x}")
    if message != []:
        print_message(text, message)
    
@doc_tag()
def check_less_than(*a):
    a = [ arrayify(x) for x in a ]

    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x < y, 
                             lambda x,y: f"{pvalue(x)} >= {pvalue(y)}")
    if message != []:
        print_message(text, message)    

@doc_tag()
def check_less_than_or_equal(*a):
    a = [ arrayify(x) for x in a ]

    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x <= y, 
                             lambda x,y: f"{pvalue(x)} > {pvalue(y)}")
    if message != []:
        print_message(text, message)
        
@doc_tag()
def check_type(a, t):
    a = [ arrayify(x) for x in a ]

    text = source_for_check_call()
    args = arguments_from_check_call(text) 
    if type(a) is not t:
        term,value = term_and_value(args[0], a)
        print_message(text, f"{term + ' and ' if term is not None else ''}{pvalue(a)} has type {type(a).__name__}, not {t.__name__}")

@doc_tag()
def check_in(a, *r):
    a = [ arrayify(x) for x in a ]

    text = source_for_check_call()
    args = arguments_from_check_call(text) 
    if len(r) == 1:
        r = arrayify(r[0])
    if a not in r:
        term,value = term_and_value(args[0], a)
        print_message(source_for_check_call(), 
                      f"{term + ' and ' if term is not None else ''}{pvalue(a)} is not in {short_form_for_value(r)}")
                
@doc_tag()
def check_between(a, *interval):
    a = [ arrayify(x) for x in a ]
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)

    message = interval_check(args, a, interval,
                             lambda a,interval: np.logical_and(interval[0] <= a, a < interval[1]))
    if message != []:
        print_message(text, message)
    
# Negations

@doc_tag("check")
def check_not(a):
    a = arrayify(a)    
    if np.all(a):
        print_message(source_for_check_call(), "Expression is True but should be False")
                
@doc_tag()
def check_not_equal(a, b):
    a = arrayify(a)
    b = arrayify(b)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)            
    message = binary_check(args, [a, b], 
                           lambda x,y: x != y, 
                           lambda x,y: f"{pvalue(x)} == {pvalue(y)}")            
    if message != []:
        print_message(text, message)
    
@doc_tag("check_close")
def check_not_close(a, b, plus_or_minus=1e-5):
    a = arrayify(a)
    b = arrayify(b)

    text = source_for_check_call()
    args = arguments_from_check_call(text)        
    message = binary_check(args, [a, b], 
                           lambda x,y: not np.isclose(x,y,atol=plus_or_minus), 
                           lambda x,y: f"{y-plus_or_minus} <= {x} <= {y+plus_or_minus}")
    if message != []:
        print_message(text, message)
    
@doc_tag("check_less_than")
def check_not_less_than(*a):
    a = [ arrayify(x) for x in a ]
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x >= y, 
                             lambda x,y: f"{pvalue(x)} < {pvalue(y)}")
    if message != []:
        print_message(text, message)    

@doc_tag("check_less_than_or_equal")
def check_not_less_than_or_equal(*a):
    a = [ arrayify(x) for x in a ]
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x > y, 
                             lambda x,y: f"{pvalue(x)} <= {pvalue(y)}")
    if message != []:
        print_message(text, message)
        
@doc_tag("check_type")
def check_not_type(a, t):
    a = arrayify(a)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text) 
    if type(a) is t:
        term,value = term_and_value(args[0], a)        
        print_message(text, f"{term + ' and ' if term is not None else ''}{pvalue(a)} has type {t.__name__}")

@doc_tag("check_in")
def check_not_in(a, *r):
    a = arrayify(a)
    
    if len(r) == 1:
        r = arrayify(r[0])
    if a in r:
        term,value = term_and_value(args[0], a)
        print_message(source_for_check_call(), 
                      f"{term + ' and ' if term is not None else ''}{pvalue(a)} is in {short_form_for_value(r)}")        
                
@doc_tag("check_between")
def check_not_between(a, *interval):
    a = arrayify(a)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)
    
    try:
        interval = grab_interval(*interval)
    except ValueError as error:
        print_message(text, str(error))
        return
    
    result = np.logical_or(not (interval[0] <= a), not(a < interval[1]))
    
    if not np.all(result):
        shape = np.shape(result)
        if len(shape) == 1:
            message = [ ]
            false_indices = np.where(result == False)[0]
            for i in false_indices[0:3]:
                ai,av = term_and_value_at_index(args[0],a,i)
                if ai != None:
                    terms = ai + " and "
                else:
                    terms = ""
                message += [ f"{terms}{pvalue(av)} is in interval [{interval[0]},{interval[1]})" ]
            if len(false_indices) > 3:
                message += [ f"... omitting {len(false_indices)-3} more case(s)" ]
        else:
            message = [ f"{pvalue(a)} is in interval [{interval[0]},{interval[1]})" ]
        print_message(text, message)
    












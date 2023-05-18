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
           'check_not_type',
           'approx',
           'between',
           'between_or_equal'       
          ]

import traceback
import numpy as np
from textwrap import indent
from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic, needs_local_scope)
from ast import *

from .docs import doc_tag

def in_otter():
    for frame in traceback.StackSummary.extract(traceback.walk_stack(None)):
        if frame.filename.endswith('ok_test.py'):
            return True
    return False

def print_message(test, message):
    # print(message)
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
    tree = parse(test_line, mode='eval')
    args = [ test_line[x.col_offset:x.end_col_offset].strip() for x in tree.body.args]
    return args
    
    
def source_for_check_call():
    # The frame with the test call is the third from the top if we call 
    # a test function directly
    # Actually fourth with the doc tags...
    tbo = traceback.extract_stack()
    assert tbo[-4].line, "The cs104 library should only be used inside a Jupyter notebook or ipython..."
    return tbo[-4].line

def pvalue(x):
    """Print a value in a readable way, either via repr or via an abbreviated np-array."""
    t = type(x)
    if t not in [ list, tuple, np.array ]:
        return repr(x)
    else:
        return np.array2string(np.array(x),separator=',',threshold=10)

def short_form_for_value(x):
    # x may be a list or array, so make sure an array...
    return np.array2string(np.array(x),separator=',',threshold=10)

def term_and_value(arg, value):
    if arg == repr(value):
        return None, value
    else:
        return f"{arg} == {pvalue(value)}", value

def term_and_value_at_index(arg, value, index):
    if type(value == tuple):
        value = list(value)
    if arg == repr(value):
        return None, value
    elif np.shape(value) == ():
        return f"{arg} == {pvalue(value)}", value
    else:
        value = np.array(value)
        return f"{arg}.item({index}) == {pvalue(value.item(index))}", value.item(index)

def arrayify(x):
    if type(x) == list or type(x) == tuple:
        return np.array(x)  
    else:
        return x
    
def binary_check(args_source, args_values, test_op, test_str):
    message = ensure_not_dots(args_source, args_values)
    if message != []:
        return message

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
            
def interval_check(args_source, a, interval, test_op, test_str):
    message = ensure_not_dots(args_source, [a, interval])
    if message != []:
        return message
    
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
                message += [ f"{terms}{pvalue(av)}{test_str(interval)}" ]
            if len(false_indices) > 3:
                message += [ f"... omitting {len(false_indices)-3} more case(s)" ]
        else:
            message = [ f"{pvalue(a)}{test_str(interval)}" ]
        return message
    else:
        return []


    
def ordering_check(args, a, compare_fn, message_fn):

    # Do the ordering check here to avoid repeated messages about
    #  same ... in a.
    message = ensure_not_dots(args, a)
    if message != []:
        return message

    for i in range(len(a)-1):
        m = binary_check(args[i:i+2], a[i:i+2], compare_fn, message_fn)            
        if len(m) > 0 and len(message) > 0:
            message += [ "" ]
        message += m
    return message  

def ensure_not_dots(args, values):
    message = []
    for a,v in zip(args, values):
        if (a != "...") and (v is ...):
            message += [ f'{a} should not be ...']
    return message

### Entry points

def _check(a):
    a = arrayify(a)
    text = source_for_check_call()
    args = arguments_from_check_call(text)     

    message = ensure_not_dots(args, [a])
    if message != []:
        print_message(text, message) 
        return

    if not np.all(a):
        print_message(text, f"Expression is not True")
                
@doc_tag()
def check_equal(a, b):
    a,b = arrayify(a),arrayify(b)
    
    try:
        text = source_for_check_call()
        args = arguments_from_check_call(text) 

        message = binary_check(args, [a, b], 
                               lambda x,y: x == y, 
                               lambda x,y: f"{pvalue(x)} != {pvalue(y)}")       
    except Exception as e:
        text = "Error: Cannot find source code"
        message = [ str(e) ]
        raise e
        
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
def check_greater_than(*a):
    a = [ arrayify(x) for x in a ]

    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x > y, 
                             lambda x,y: f"{pvalue(x)} <= {pvalue(y)}")
    if message != []:
        print_message(text, message)    

@doc_tag()
def check_greater_than_or_equal(*a):
    a = [ arrayify(x) for x in a ]

    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x >= y, 
                             lambda x,y: f"{pvalue(x)} < {pvalue(y)}")
    if message != []:
        print_message(text, message)


@doc_tag()
def check_type(a, t):
    text = source_for_check_call()
    args = arguments_from_check_call(text) 

    message = ensure_not_dots([args[0]], [a])
    if message != []:
        print_message(text, message)
        return

    ts = t
    if t == float:
        ts = ( np.floating, float )
    if t == int:
        ts = ( np.integer, int )


    if not isinstance(a, ts):
        term,value = term_and_value(args[0], a)
        print_message(text, f"{term + ' and ' if term is not None else ''}{pvalue(a)} has type {type(a).__name__}, not {t.__name__}")

@doc_tag()
def check_in(a, *r):
    a = arrayify(a)

    text = source_for_check_call()
    args = arguments_from_check_call(text) 

    message = ensure_not_dots(args, [a, *r])
    if message != []:
        print_message(text, message)
        return

    if len(r) == 1:
        r = arrayify(r[0])
    if a not in r:
        term,value = term_and_value(args[0], a)
        print_message(text, 
                      f"{term + ' and ' if term is not None else ''}{pvalue(a)} is not in {short_form_for_value(r)}")
                
@doc_tag()
def check_between(a, *interval):
    a = arrayify(a)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)

    message = interval_check(args, a, interval,
                             lambda a,interval: np.logical_and(interval[0] <= a, a < interval[1]),
                             lambda interval: f" is not in interval [{interval[0]},{interval[1]})")
    if message != []:
        print_message(text, message)

@doc_tag()
def check_between_or_equal(a, *interval):
    a = arrayify(a)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)

    message = interval_check(args, a, interval,
                             lambda a,interval: np.logical_and(interval[0] <= a, a <= interval[1]),
                             lambda interval: f" is not in interval [{interval[0]},{interval[1]}]")
    if message != []:
        print_message(text, message)

# Negations

@doc_tag("check")
def check_not(a):
    a = arrayify(a)    
    text = source_for_check_call()
    args = arguments_from_check_call(text)        

    message = ensure_not_dots(args, [a])
    if message != []:
        print_message(text, message)
        return

    if np.all(a):
        print_message(source_for_check_call(), f"{pvalue(args)} is True but should be False")
                
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

@doc_tag("check_greater_than")
def check_not_greater_than(*a):
    a = [ arrayify(x) for x in a ]
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x <= y, 
                             lambda x,y: f"{pvalue(x)} > {pvalue(y)}")
    if message != []:
        print_message(text, message)    

@doc_tag("check_greater_than_or_equal")
def check_not_less_than_or_equal(*a):
    a = [ arrayify(x) for x in a ]
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)    
    message = ordering_check(args, a, 
                             lambda x,y: x < y, 
                             lambda x,y: f"{pvalue(x)} >= {pvalue(y)}")
    if message != []:
        print_message(text, message)


@doc_tag("check_type")
def check_not_type(a, t):
    text = source_for_check_call()
    args = arguments_from_check_call(text) 

    message = ensure_not_dots([args[0]], [a])
    if message != []:
        print_message(text, message)
        return

    if type(a) is t:
        term,value = term_and_value(args[0], a)        
        print_message(text, f"{term + ' and ' if term is not None else ''}{pvalue(a)} has type {t.__name__}")

@doc_tag("check_in")
def check_not_in(a, *r):
    a = arrayify(a)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text) 
    message = ensure_not_dots(args, [a, *r])
    if message != []:
        print_message(text, message)
        return
    
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

    message = interval_check(args, a, interval,
                             lambda a,interval: np.logical_or(not (interval[0] <= a), not(a < interval[1])),
                             lambda interval: f" is in interval [{interval[0]},{interval[1]})")
    if message != []:
        print_message(text, message)
    

@doc_tag("check_between_or_equal")
def check_not_between_or_equal(a, *interval):
    a = arrayify(a)
    
    text = source_for_check_call()
    args = arguments_from_check_call(text)

    message = interval_check(args, a, interval,
                             lambda a,interval: np.logical_or(not (interval[0] <= a), not(a <= interval[1])),
                             lambda interval: f" is in interval [{interval[0]},{interval[1]}]")
    if message != []:
        print_message(text, message)







###############


ops = {
    Eq     : (lambda x,y: x == y, "==", NotEq),
    NotEq  : (lambda x,y: x != y, "!=", Eq),
    Lt     : (lambda x,y: x < y, "<", GtE),
    LtE    : (lambda x,y: x <= y, "<=", Gt),
    Gt     : (lambda x,y: x > y, ">", LtE),
    GtE    : (lambda x,y: x >= y, ">=", Lt),
    Is     : (lambda x,y: x is y, "is", IsNot),
    IsNot  : (lambda x,y: x is not y, "is not", Is),
    In     : (lambda x,y: x in y, "in", NotIn),
    NotIn  : (lambda x,y: x not in y, "not in", In)
}

def is_compare(op):
    return type(op) in ops

def eval_op(op, left, right):
    return ops[type(op)][0](left, right)

def to_string(op):
    return ops[type(op)][1]

def negate(op):
    return ops[type(op)][2]()

def norm(x):
    if type(x) == list or type(x) == tuple:
        x = np.array(x)  
    if type(x) == type:
        return x.__name__
    if type(x) != np.array:
        return str(x)
    else:
        return np.array2string(x,separator=',',threshold=10)


###
#
# e ::=  And(e+) | Or(e+) | Not(e) | t
# t ::=  Rel(u, ops+, u+) | term
#
def eval_check(line, local_ns=None):
    def text_for(x):
        return get_source_segment(line, x)
        
    def eval_node(x):
        result = eval(compile(text_for(x), '', 'eval'), globals(), local_ns)
        if result is ... or result is type(...):
            raise ValueError(f"{text_for(x)} should not be ...")
        return result

    def operand_message(x, x_value, index = None):
        if index != None and type(x_value) in [ list, tuple, np.ndarray ]:
            ivalue = norm(x_value[index])
            return f'{unparse(x)}[{index}] == {ivalue} and ', ivalue
        elif type(x) != Constant and unparse(x) != repr(x_value):
            value = norm(x_value)
            return f'{unparse(x)} == {value} and ', value
        else:
            return '', norm(x_value)

    def failed_message(left, left_value, right, right_value, op, index = None):
        lm, lv = operand_message(left, left_value, index)
        rm, rv = operand_message(right, right_value, index)
        return f'{lm}{rm}{lv} {to_string(negate(op))} {rv}'
    
    def eval_comparison(left, left_value, op, right, right_value):
        result = eval_op(op, left_value, right_value)
        if not np.all(result):
            message = [ ] 
            shape = np.shape(result)
            if len(shape) != 1:
                message += [ failed_message(left, left_value, right, right_value, op) ]
            else:
                false_indices = np.where(result == False)[0]
                for i in false_indices[0:3]:
                    message += [ failed_message(left, left_value, right, right_value, op, i) ]
                if len(false_indices) > 3:
                    message += [ f"... omitting {len(false_indices)-3} more case(s)" ]
            return [ f'{text_for(left)} {to_string(op)} {text_for(right)} is false because' ] + [ '  ' + m for m in message ]
        return [ ]

    def eval_term(x):
        if type(x) is Compare:
            message = [ ]
            left = x.left
            left_value = eval_node(left)
            for op,right in zip(x.ops, x.comparators):
                right_value = eval_node(right)
                message += eval_comparison(left, left_value, 
                                           op,
                                           right, right_value)
                left, left_value = right, right_value
            return message
        elif not eval_node(x):
            return [ 'Expression is not true' ]
        else:
            return [ ]


    def eval_expr(x, depth = 0):
        t = type(x)
        if t is BoolOp:
            op = type(x.op)
            results = [ eval_expr(y, depth + 1) for y in x.values ]
            if op == And:
                message = [ ]
                for expr,result in zip(x.values, results):
                    if result != [ ]:
                        message += [ f'{"  " * (depth)}{x}' for x in result ]
                return message
            elif op == Or and not np.any([ r == [ ] for r in results]):
                message = [ ]
                for expr,result in zip(x.values, results):
                    message += [ f'{"  " * (depth)}{x}' for x in result ]
                return message
            else:
                return [ ]
        elif t is UnaryOp and type(x.op) == Not:
            result = eval_expr(x.operand, depth + 1)
            if result == [ ]:
                return [  f'{"  " * depth}{text_for(x)} is false because',
                          f'{"  " * (depth+1)}{text_for(x.operand)} is true']
            else: 
                return [ ]
        else:
            return eval_term(x)
        
    a = parse(line, mode='eval')
    return eval_expr(a.body)

@register_line_magic
@needs_local_scope
def check(line, local_ns=None):
    if type(line) == bool:
        # dispatch to old version...
        _check(line)
    else:
        try:
            message = eval_check(line.lstrip(), local_ns)
        except SyntaxError as e:
            message = [ f"SyntaxError: {e.args[0]}", f"{e.text}", f"{' '*(e.offset-1)}^" ]
        except Exception as e:
            message = [ str(e) ]
            
        if message != [ ]:
            print_message(f'check failed: {line}', message)          
           
@register_line_magic
@needs_local_scope
def assert_true(line, local_ns=None):
    message = eval_check(line, local_ns)
    assert message == [ ]

@register_line_magic
@needs_local_scope
def assert_false(line, local_ns=None):
    message = eval_check(line, local_ns)
    assert message != [ ]


class approx:
    def __init__(self, a, plus_or_minus=1e-5):
        if type(a) not in [ np.number, int, float ]:
            raise ValueError(f"Can only approximate numeric values, not {repr(a)}")

        self.a = a
        self.plus_or_minus = plus_or_minus

    def __str__(self):
        #return f'{self.a} ± {np.format_float_positional(self.plus_or_minus)}'
        return f'({self.a} ± {np.format_float_positional(self.plus_or_minus)})'
    
    def __repr__(self):
        return f'approx({self.a})'

    def __eq__(self, v):
        print(v, self.a, type(v), type(self.a))
        return np.isclose(v,self.a,atol=self.plus_or_minus)



class between:
    def __init__(self, lo, hi,):
        if type(lo) not in [ np.number, int, float ]:
            raise ValueError(f"Can only create interval with numeric values, not {repr(lo)}")
        if type(hi) not in [ np.number, int, float ]:
            raise ValueError(f"Can only create interval with numeric values, not {repr(hi)}")

        self.lo = lo
        self.hi = hi

    def __str__(self):
        return f'[{self.lo},{self.hi})'

    def __repr__(self):
        return f'between({self.lo}, {self.hi})'

    def __contains__(self, v):
        return self.lo <= v < self.hi

class between_or_equal:
    def __init__(self, lo, hi,):
        if type(lo) not in [ np.number, int, float ]:
            raise ValueError(f"Can only create interval with numeric values, not {repr(lo)}")
        if type(hi) not in [ np.number, int, float ]:
            raise ValueError(f"Can only create interval with numeric values, not {repr(hi)}")

        self.lo = lo
        self.hi = hi

    def __repr__(self):
        return f'between_or_equal({self.lo}, {self.hi})'

    def __str__(self):
        return f'[{self.lo},{self.hi}]'

    def __contains__(self, v):
        return self.lo <= v <= self.hi

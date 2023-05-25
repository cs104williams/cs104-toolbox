__all__ = ['check', 'check_str', 'approx', 'between', 'between_or_equal' ]

import traceback
import numpy as np
from textwrap import indent
from IPython.core.magic import (register_line_magic, register_cell_magic,
                                register_line_cell_magic, needs_local_scope)
from IPython import get_ipython

from ast import *
import abc

from .docs import doc_tag

def in_otter():
    """Test whether or not we are running inside Otter"""
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

def source_for_check_call():
    # The frame with the test call is the third from the top if we call 
    # a test function directly
    # Actually fourth with the doc tags...
    tbo = traceback.extract_stack()
    assert tbo[-4].line, "The cs104 library should only be used inside a Jupyter notebook or ipython..."
    return tbo[-4].line

### Entry points

@doc_tag
def check(a):
    print(a)
    """Verify that condition a is True, and print a warning message if it is not.
       The parameter a can be a boolean expression or an array of booleans."""
    text = source_for_check_call()
    if not np.all(a):
        print_message(text, f"Expression is not True")

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
    if type(x) == type or type(x) == abc.ABCMeta:
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
        # return type of how x was computed along with a normalized value string
        if index != None and type(x_value) in [ list, tuple, np.ndarray ]:
            ivalue = norm(x_value[index])
            return f'{unparse(x)}[{index}] == {ivalue} and ', ivalue
        elif type(x) != Constant and unparse(x) != norm(x_value):
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
            if (op == And) or (op == Or and not np.any([ r == [ ] for r in results])):
                return [ f'{"  " * (depth)}{x}' for result in results for x in result ]
            else:
                return [ ]
        elif t is UnaryOp and type(x.op) == Not:
            if eval_expr(x.operand, depth + 1) == [ ]:
                return [  f'{"  " * depth}{text_for(x)} is false because',
                          f'{"  " * (depth+1)}{text_for(x.operand)} is true']
            else: 
                return [ ]
        else:
            return eval_term(x)
        
    a = parse(line, mode='eval')
    return eval_expr(a.body)

def check_str(a, local_ns=None):
    """Evaluates the expression a, and print a warning message if it is not true.
       The parameter a can be any string evaluating a boolean expression or an array of booleans in the
       local context local_ns."""
    try:
        message = eval_check(a.lstrip(), local_ns)
        # These two lines are a sanity check -- remove after we're sure it all works...
        just_eval_result = np.all(eval(compile(a.lstrip(), '', 'eval'), local_ns))
        assert (message == [ ]) == just_eval_result
    except SyntaxError as e:
        message = [ f"SyntaxError: {e.args[0]}", f"{e.text}", f"{' '*(e.offset-1)}^" ]
    except Exception as e:
        message = [ str(e) ]
        
    if message != [ ]:
        print_message(f'check({a})', message)

    return None       

# Install a transformer that converts any call to check() into 
# a call to check_str().  This enables us to use our own evaluator
# when we are in an ipython environment.           
ip = get_ipython()
if ip != None:
    import re
    def checkify(lines):
        new_lines = []
        for line in lines:
            m = re.match(r'check\((.*)\)', line)
            if m:
                escaped = m.group(1).replace("'", "\\'")
                new_lines.append(f"check_str('{escaped}', locals())")
            else:
                new_lines.append(line)
        return new_lines

    ip.input_transformers_cleanup.append(checkify)           



class approx:
    def __init__(self, a, plus_or_minus=1e-5):
        if type(a) not in [ np.number, int, float ]:
            raise ValueError(f"Can only approximate numeric values, not {repr(a)}")

        self.a = a
        self.plus_or_minus = plus_or_minus

    def __str__(self):
        return f'({self.a} ± {np.format_float_positional(self.plus_or_minus)})'
    
    def __repr__(self):
        return f'approx({self.a})'

    def __eq__(self, v):
        return np.isclose(v,self.a,atol=self.plus_or_minus)



class between:
    def __init__(self, lo, hi):
        for x in (lo, hi):
            if type(x) not in [ np.number, int, float ]:
                raise ValueError(f"Can only create interval with numeric values, not {repr(x)}")

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
        for x in (lo, hi):
            if type(x) not in [ np.number, int, float ]:
                raise ValueError(f"Can only create interval with numeric values, not {repr(x)}")

        self.lo = lo
        self.hi = hi

    def __repr__(self):
        return f'between_or_equal({self.lo}, {self.hi})'

    def __str__(self):
        return f'[{self.lo},{self.hi}]'

    def __contains__(self, v):
        return self.lo <= v <= self.hi

"""
Support for writing tests, including a general check function that prints
a reasonable error message if a test fails and supporting objects to 
represent approximate values and intervals.
"""

__all__ = ['check', 'check_str', 'approx', 'between', 'between_or_equal' ]

import traceback
import numpy as np
from textwrap import indent
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
    """Reports an error message for a failed test.  Both test 
    and message should be strings.  This function prints plain text 
    when running inside the otter grader.  Otherwise it includes
    ANSI color codes and emojis..."""

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
    """
    The frame with the test call is the third from the top if we call 
    a test function directly.
    Actually fourth with the doc tags...
    """
    tbo = traceback.extract_stack()
    if tbo[-4].line == "":
        return "Failed check"
    else:
        return tbo[-4].line

### Entry points

@doc_tag()
def check(condition):
    """
    Verify that condition is True, and print a warning message if it is not.
    The condition can be a boolean expression or an array of booleans.
    """
    text = source_for_check_call()
    if type(condition) == bool or \
        type(condition) == np.ndarray and condition.dtype == bool:
        if not np.all(condition):
            print_message(text, f"Expression is not True")
    else:
        raise ValueError("Argument to check should not be a boolean or array of booleans")


###############

# A little interpreter for Python ASTs representing boolean expressions.

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
    """
    Normalize the output of lists/tuples/arrays, and avoid printing
    values that are waaay too long.
    """
    if type(x) == list or type(x) == tuple:
        x = np.array(x)  
    if type(x) == type or type(x) == abc.ABCMeta:
        return x.__name__
    if type(x) != np.ndarray:
        return str(x)
    else:
        return np.array2string(x,separator=',',threshold=10)

def eval_check(line, local_ns=None):
    """
    An evaluator for boolean expressions from the Python grammer:
    
        e ::=  And(e+) | Or(e+) | Not(e) | t
        t ::=  Rel(u, ops+, u+) | term

    local_ns should be the value of variables appearing in the line of code.
    Returns a list of lines making up an error message, if the expression is False,
    or an empty list of the expression is True.
    """

    def text_for(x):
        """
        Return the source text corresponding to an AST node x.
        """
        return get_source_segment(line, x)
        
    def eval_node(x):
        """
        Evaluate the AST node x.
        """
        result = eval(compile(text_for(x), '', 'eval'), globals(), local_ns)

        # special error if one of the variables is ..., and not be design
        if text_for(x) != '...' and (result is ... or result is type(...)):
            raise ValueError(f"{text_for(x)} should not be ...")
        
        return result

    def operand_message(x, x_value, index = None):
        """
        Return a string showing the value of variable x or index term x[i],
        as well as the value computed by that expr.  Use normalized value strings
        to avoid too much output...
        """
        if index != None and type(x_value) in [ list, tuple, np.ndarray ]:
            ivalue = norm(x_value[index])
            return f'{unparse(x)}[{index}] == {ivalue} and ', ivalue
        elif type(x) != Constant and type(x_value) not in [ approx, between, between_or_equal ] and unparse(x) != norm(x_value):
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
            return [ f'{text_for(left)} {to_string(op)} {text_for(right)} is false because' ] + \
                   [ '  ' + m for m in message ]
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
    """
    Evaluates the expression a, and print a warning message if it is not true.
    The parameter a can be any string evaluating a boolean expression or an array of booleans in the
    local context local_ns.
    
    **Note:** this is intended to only be used internally by the cs104 library, and
    only when running tests inside Jupyter notebooks.  Never call this function directly!
    
    """
    try:
        message = eval_check(a.lstrip(), local_ns)
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
try:
    from IPython import get_ipython
    ip = get_ipython()
    if ip != None:
        import re
        def checkify(lines):
            new_lines = []
            for line in lines:
                m = re.match(r'check\((.*)\)', line)
                if m:
                    escaped = m.group(1).replace("'", "\\'")
                    new_lines.append(f"check_str('{escaped}', locals())\n")
                else:
                    new_lines.append(line)
            return new_lines

        ip.input_transformers_cleanup.append(checkify)           
except NameError:
    pass



class approx:
    """
    An approximate number.  Useful to capture numerical error or uncertainty 
    of a measurement when testing conditions:

    * check(x == approx(1))        # check if x is 1 ± 1e-5
    * check(x == approx(1000, 20)) # check if x is 1000 ± 20
    """
    def __init__(self, a, plus_or_minus=1e-5):
        """
        Create an approximate number a ± plus_or_minus
        """
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
    """
    An half-closed interval useful when testing conditions:

    * check(x in between(0,1))     # check if x in [0,1)
    * check(x in between(0,10))    # check if x in [0,10)
    """

    def __init__(self, lo, hi):
        """
        Create a half-closed interval [lo, hi).
        """
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
    """
    A closed interval useful when testing conditions:

    * check(x in between_or_equal(0,1))     # check if x in [0,1]
    * check(x in between_or_equal(0,10))    # check if x in [0,10]
    """

    def __init__(self, lo, hi):
        """
        Create a closed interval [lo, hi].
        """
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

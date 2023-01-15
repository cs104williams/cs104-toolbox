import uuid
import traceback
from IPython.core.display import display, HTML
from IPython.utils.text import strip_ansi
from IPython import get_ipython


def shorten_stack(shell, etype, evalue, tb, tb_offset=None): 
    id = uuid.uuid1().hex
    full = strip_ansi(shell.InteractiveTB.stb2text(shell.InteractiveTB.structured_traceback(etype, evalue, tb, tb_offset)))
    
    for s in traceback.walk_tb(tb):
        filename = s[0].f_code.co_filename
        if "datascience" in filename or \
            "cs104" in filename or \
            "site-packages" in filename :
            s[0].f_locals['__tracebackhide__'] = 1

    shell.showtraceback((etype, evalue, tb), tb_offset)
    
    text = f"""
    <div align="right">
        <a style='inherit;font-size:12px;' onclick='var x = document.getElementById("{id}"); if (x.style.display === "none") x.style.display = "block"; else x.style.display = "none";'>Full Details</a>
    </div>
    <pre style="font-size:14px;display:none; background-color:#FFDDDD;" id="{id}">{full}</pre>
    """

    display(HTML(text))
    
# this registers a custom exception handler for the whole current notebook
ipy = get_ipython()
if ipy != None:
    ipy.set_custom_exc((Exception,), shorten_stack)
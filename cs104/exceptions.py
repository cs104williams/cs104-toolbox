import uuid
import traceback
from IPython.core.display import display, HTML
from IPython.utils.text import strip_ansi

def shorten_stack(shell, etype, evalue, tb, tb_offset=None): 
    id = uuid.uuid1().hex
    full = strip_ansi(shell.InteractiveTB.stb2text(shell.InteractiveTB.structured_traceback(etype, evalue, tb, tb_offset)))

    # The files for each frame in the traceback:
    #   * files[0] will always be the ipython entry point
    #   * files[1] will always be in the notebook
    files = [ frame.filename for frame in traceback.extract_tb(tb) ]
    
    # Find the top-most frame that corresponds to the notebook.  We will
    #  ignore all the frames above that, since the code is not meaningful
    #  to us.
    notebook_filename = files[1]
    last_notebook_filename = len(files) - 1
    while last_notebook_filename > 0 and files[last_notebook_filename] != notebook_filename:
        last_notebook_filename -= 1
    
    # Go the the last notebook frame and drop the rest
    tail = tb
    for i in range(last_notebook_filename):
        tail = tail.tb_next
    tail.tb_next = None
    
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
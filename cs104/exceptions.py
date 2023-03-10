__all__ = []

import uuid
import traceback
from IPython.core.display import display, HTML
from IPython.utils.text import strip_ansi
from ansi2html import Ansi2HTMLConverter

def is_user_file(filename):
    return "/datascience" not in filename and \
           '/site-packages' not in filename and \
           '/cs104' not in filename

html_prefix = \
 """<style type="text/css">
    .ansi2html-content { display: inline; white-space: pre-wrap; word-wrap: break-word; }
    .body_foreground { color: #3e424d; }
    .body_background { background-color: #FFDDDD; }
    .ansi1 { font-weight: bold; }
    .ansi31 { color: #e75c58; }
    .ansi32 { color: #00a250; }
    .ansi34 { color: #208ffb; }
    .ansi36 { color: #60c6c8; }
    </style>"""

def shorten_stack(shell, etype, evalue, tb, tb_offset=None): 
    id = uuid.uuid1().hex
    
    # Take the full stack trace and convert into HTML.  
    conv = Ansi2HTMLConverter()
    itb = shell.InteractiveTB
    ansi = "".join(itb.stb2text(itb.structured_traceback(etype, evalue, tb, tb_offset)))
    full = conv.convert(ansi, full=False)
    full = html_prefix + full
    
    # The files for each frame in the traceback:
    #   * files[0] will always be the ipython entry point
    #   * files[1] will always be in the notebook
    files = [ frame.filename for frame in traceback.extract_tb(tb) ]
    
    # Find the top-most frame that corresponds to the notebook.  We will
    #  ignore all the frames above that, since the code is not meaningful
    #  to us.
    notebook_filename = files[1]
    last_notebook_filename = len(files) - 1
    while last_notebook_filename > 0 and not is_user_file(files[last_notebook_filename]):
        last_notebook_filename -= 1

    # Go the the last notebook frame and drop the rest
    tail = tb
    for i in range(last_notebook_filename):
        tail = tail.tb_next
    tail.tb_next = None
                
    # Hide any stack frames in the middle of the traceback
    #  that correspond to library code, using the sneaky
    #  special var trick.
    for f in traceback.walk_tb(tb):
        frame = f[0]
        filename = frame.f_code.co_filename
        if not is_user_file(filename):
            locals = frame.f_locals
            locals['__tracebackhide__'] = 1

    # Show the stack trace in stderr
    shell.showtraceback((etype, evalue, tb), tb_offset)
    
    # Make the HTML full version we can show with a click.
    text = f"""
        <div align="right">
            <a style='inherit;font-size:12px;' 
               onclick='var x = document.getElementById("{id}"); \
               if (x.style.display === "none") \
                 x.style.display = "block"; \
                 else x.style.display = "none";'> \
              Full Details
            </a>
        </div>
        <pre style="font-size:14px;display:none; \
                    color: #3e424d;  \
                    background-color:#FFDDDD;" 
             id="{id}">{full}</pre>
    """
    display(HTML(text))
    
# this registers a custom exception handler for the whole current notebook
ipy = get_ipython()
if ipy != None:
    ipy.set_custom_exc((Exception,), shorten_stack)
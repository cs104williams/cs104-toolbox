"""
Better exception reporting.  Error messages will hide stack frames
not written by the user and insert documentation links when the
error occurs while in a function associated with a url via the
docs.py code.

Set the CS104_DISABLE_EXC_FORMAT environment variable to 1 to 
disable this feature.
"""

__all__ = []

import os
import traceback
import uuid
from textwrap import dedent

from ansi2html import Ansi2HTMLConverter
from IPython.core.display import HTML, display
from IPython.core.getipython import get_ipython

from . import context


# Code we can assume the user wrote.
def _is_user_file(filename):
    return (
        "/datascience" not in filename
        and "/site-packages" not in filename
        and "/cs104" not in filename
        and ".pyx" not in filename
    )


# Needed for ansi colors to work in the html we generate
_html_prefix = """
<style type="text/css">
.ansi2html-content { display: inline; white-space: pre-wrap; word-wrap: break-word; }
.body_foreground { color: #3e424d; }
.body_background { background-color: #FFDDDD; }
.ansi1 { font-weight: bold; }
.ansi31 { color: #e75c58; }
.ansi32 { color: #00a250; }
.ansi34 { color: #208ffb; }
.ansi36 { color: #60c6c8; }
</style>
"""


def _shorten_stack(shell, etype, evalue, tb, tb_offset=None):
    """
    Unwind the stack back to the last function the user wrote, hide any
    intermediate frames from libraries, insert doc link, and wrap up all that
    in an HTML formatted error message.
    """
    itb = shell.InteractiveTB
    id = uuid.uuid1().hex

    # Take the full stack trace and convert into HTML.
    conv = Ansi2HTMLConverter()
    ansi = "".join(itb.stb2text(itb.structured_traceback(etype, evalue, tb, tb_offset)))
    full = conv.convert(ansi, full=False)
    full = _html_prefix + full

    # if we biff anywhere, default to just showing the original message.
    frames = traceback.extract_tb(tb)

    # The files for each frame in the traceback:
    #   * files[0] will always be the ipython entry point
    #   * files[1] will always be in the notebook
    files = [frame.filename for frame in frames]

    # Find the top-most frame that corresponds to the notebook.  We will
    #  ignore all the frames above that, since the code is not meaningful
    #  to us.
    notebook_filename = files[1]
    last_tb_from_notebook_index = len(files) - 1
    while last_tb_from_notebook_index > 0 and not _is_user_file(
        files[last_tb_from_notebook_index]
    ):
        last_tb_from_notebook_index -= 1

    # Go the the last notebook frame and drop the rest
    tail = tb
    for i in range(last_tb_from_notebook_index):
        tail = tail.tb_next
    callee = tail.tb_next
    tail.tb_next = None

    see_also = ""
    if callee != None:
        locals = callee.tb_frame.f_locals
        url = locals.get("__doc_url__", None)
        if url != None:
            see_also = f'<strong>>>>>> See also the <a href="{url}">docs for {url[url.index("#")+1:]}</a></strong>'

    # Hide any stack frames in the middle of the traceback
    #  that correspond to library code, using the sneaky
    #  special var trick.
    for f in traceback.walk_tb(tb):
        frame = f[0]
        filename = frame.f_code.co_filename
        if not _is_user_file(filename):
            locals = frame.f_locals
            locals["__tracebackhide__"] = 1

    # Show the stack trace in stderr
    shell.showtraceback((etype, evalue, tb), tb_offset)

    if context.in_jupyter() and os.getenv("CS104_DISABLE_EXC_FORMAT", "0") != "1":
        # Add the doc link, as well as a link to show the full stack trace.
        text = dedent(
            f"""
            <div class="m-2" style="padding-left: 5px; margin-right: -20px; padding-top:20px; padding-bottom:5px; background-color:#FFDDDD;">
                {see_also}
            </div> 
            <div align="right" style="margin-right: -20px;"> \
                <a style='inherit;font-size:12px;'  \
                onclick='var x = document.getElementById("{id}"); \
                if (x.style.display === "none") \
                    x.style.display = "block"; \
                    else x.style.display = "none";'> \
                Full Details
                </a>
            </div>
            <pre style="margin-right: -20px; \
                        font-size:14px;display:none; \
                        color: #3e424d;  \
                        background-color:#FFDDDD;" \
                id="{id}">{full}</pre>
            """
        )
        display(HTML(text))


def _safe_shorten_stack(shell, etype, evalue, tb, tb_offset=None):
    """
    A wrapper that catches all exceptions created while processing
    an exception and punts back to the shell's default behavior.

    This ensures that, even if the shorten_stack code doesn't
    handle every case properly, some error related to the user's
    program will be shown.  (Rather than the custom TB handler failure
    message reported if we don't catch exceptions here.)

    It's possible we end up changing tb before an exception gets
    raised in shorten_stack -- so shorten_stack should never leave
    tb in a state that can't be printed...
    """
    try:
        _shorten_stack(shell, etype, evalue, tb, tb_offset)
    except Exception:
        shell.showtraceback((etype, evalue, tb), tb_offset=0)


# this registers a custom exception handler for the whole current notebook
try:
    ipy = get_ipython()
    if ipy != None:
        ipy.set_custom_exc((Exception,), _safe_shorten_stack)
except NameError:
    pass

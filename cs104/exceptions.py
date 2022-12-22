import uuid
import traceback
from IPython.core.display import display, HTML

def shorten_stack(shell, etype, evalue, tb, tb_offset=None): 
    id = uuid.uuid1().hex
    shell.InteractiveTB.color_toggle()
    full = shell.InteractiveTB.structured_traceback(etype, evalue, tb, tb_offset)
    shell.InteractiveTB.color_toggle()
    
    files = [ frame.filename for frame in traceback.extract_tb(tb) ]
    interactive_filename = files[1]
    last_interactive_frame = len(files) - 1
    while last_interactive_frame > 0 and files[last_interactive_frame] != interactive_filename:
        last_interactive_frame -= 1
    
    tail = tb
    for i in range(last_interactive_frame):
        tail = tail.tb_next
    tail.tb_next = None
    
    shell.showtraceback((etype, evalue, tb), tb_offset)
    text = '''
    <script>
        function myFunction(id) {
          var x = document.getElementById(id);
          if (x.style.display === "none") {
            x.style.display = "block";
          } else {
            x.style.display = "none";
          }
        }
    </script>

    <div align="right">
        <a style='inherit;font-size:12px;' onclick='myFunction("''' + id + '''")'>Full Details</a>
    </div>

    <pre style="font-size:14px;display:none; background-color:#FFDDDD;" id="'''+id+'''">''' + shell.InteractiveTB.stb2text(full) + '''
    </pre>
    '''
    
    display(HTML(text))
    
# this registers a custom exception handler for the whole current notebook
ipy = get_ipython()
if ipy != None:
    ipy.set_custom_exc((Exception,), shorten_stack)
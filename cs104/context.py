__all__ = []

import os
import traceback


def in_jupyter() -> bool:
    """Check if we're running in a Jupyter notebook."""
    try:
        from IPython import get_ipython

        get_ipython
        ipython = get_ipython()
        shell = ipython.__class__.__name__
        if (
            "google.colab" in str(ipython.__class__)
            or os.getenv("DATABRICKS_RUNTIME_VERSION")
            or shell == "ZMQInteractiveShell"
        ):
            return True  # Jupyter notebook or qtconsole
        elif shell == "TerminalInteractiveShell":
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)b
    except NameError:
        return False


def in_otter():
    """Test whether or not we are running inside Otter"""
    for frame in traceback.StackSummary.extract(traceback.walk_stack(None)):
        if frame.filename.endswith("ok_test.py"):
            return True
    return False

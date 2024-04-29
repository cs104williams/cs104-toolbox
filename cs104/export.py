"""
Insert a hook that saves the notebook before exporting it to avoid the common
pitfall of not saving before exporting, and thus not having all of the outputs
necessary to grade the manual questions.

Basic idea here:
https://stackoverflow.com/questions/66880698/how-to-cause-jupyter-lab-to-save-notebook-programmatically

"""

__all__ = []


from .context import in_jupyter

if in_jupyter():
    try:
        from ipylab import JupyterFrontEnd
        from ipywidgets import Output
        import otter
        import time

        _orig = otter.Notebook.export

        def _call(*args, **kwargs):
            try:
                app = JupyterFrontEnd()
                out = Output()

                def save():
                    with out:
                        print("Saving notebook...")
                        app.commands.execute("docmanager:save")
                        # There is a race condition here: The save is asynchronous,
                        # and we don't want to continue until it completes.  The
                        # sleep is annoying but delays things long enough...
                        time.sleep(5)
                        print("Exporting notebook...")
                        _orig(*args, **kwargs)

                app.on_ready(save)
                return out
            except:
                return _orig(*args, **kwargs)

        setattr(otter.Notebook, "export", _call)
    except:
        # Silently fail if we can't load the libs and install the hook.
        pass

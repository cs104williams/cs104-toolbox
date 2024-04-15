#!/usr/bin/env python
# coding: utf-8

# In[1]:


import ipywidgets
import matplotlib.pyplot as plt
import io
import numpy as np
import base64
from IPython.display import display, HTML


# In[2]:


import ipywidgets as widgets
widgets.IntSlider(
    value=7,
    min=0,
    max=10,
    step=1,
    description='Test:',
    disabled=False,
    continuous_update=False,
    orientation='horizontal',
    readout=True,
    readout_format='d'
)


# In[ ]:





# In[3]:


def f(x,y):
    return x


# In[4]:


widgets.interact(f, x=(1,10), y=['a', 'b', 'c'])


# In[5]:


# import matplotlib.pyplot as plt
# import io
# import numpy as np
# import base64
# from IPython.display import display, HTML

# def make(i):
#     # Create a plot
#     plt.figure()
#     x = np.arange(0,i)
#     plt.plot(x, x**2)  # Example data
#     plt.title("Example Plot")
#     plt.xlabel("X-axis")
#     plt.ylabel("Y-axis")
    
#     # Save the plot to a BytesIO object
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')  # Save as PNG
#     buf.seek(0)  # Move to the beginning of the buffer
#     plt.close()
    
#     # Encode the buffer to base64
#     img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

#     return "data:image/png;base64," + img_base64

# images = [ make(i) for i in range(0,6) ]

# html = """
# <style>
#   .slider-container {
#     display: flex;
#     align-items: center;
#     justify-content: center;
#     margin-bottom: 10px;  /* added space between slider and image */
#   }
#   .value-label {
#     margin-left: 10px;
#     width: 40px; /* fixed width */
#     display: inline-block; /* makes width effective */
#     text-align: right; /* aligns the number to the right */
#   }
#   img {
#     width: 400px;c
#     height: 300px;
#     display: block; /* ensures it centers in the container if needed */
#     margin: auto; /* centers the image horizontally */
#   }
# </style>
# <div class="slider-container">
#   <label for="slider">Adjust Value:</label>
#   <input type="range" id="slider" min="0" max="5" value="1">
#   <span class="value-label" id="sliderValue">1</span>
# </div>
# <img id="dynamicImage" src="" alt="Dynamic Image">

# <script>
#   var _slider = document.getElementById('slider');
#   var _sliderValue = document.getElementById('sliderValue');
#   var _dynamicImage = document.getElementById('dynamicImage');

#   var images = [ 
#     """ + ",".join([ '"' + x + '"' for x in images]) + """
#   ]

#   _slider.oninput = function() {
#     _sliderValue.textContent = this.value;
#     _dynamicImage.src = images[this.value];
#   }
# </script>
# """

# HTML(html)


# In[6]:


from datascience import *
from matplotlib import pyplot as plots
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnchoredText
import numpy as np

from IPython.display import HTML, display

import inspect
import numbers

def animate(f, gen, interval=100, default_mode=None, fig=None, show_params=True, **kwargs):
    """
    Animate a series of calls to the function f.  That function should create 
    a single plot.

    The gen parameter should be a generator function that returns a map from f's 
    parameters to their values.  Successive calls to gen returns the values for 
    successive frames.  Optional arguments:

    * interval: the time step, in ms.
    * default_mode: the mode for the player.  Options are "Once", "Repeat, "Rewind".
    * fig: pass in a matplot lib Figure if you do not want the function to create a new figure for
        the animation.
    * show_params: Show the parameters to f in a box to the side of the figure.
    * **kwargs: Any additional kwargs are pass to the constructor for Figure.  Requires fig
        to be None.
    """

    kwargs = kwargs.copy()
    kwargs.setdefault('figsize', (8, 5))
    
    if fig is None:
        fig = Figure(**kwargs)
    
    parameter_names = inspect.signature(f).parameters.keys()

    def one_frame(args):
        for ax in fig.axes():
            ax.clear()
            
        with fig:
            
            parameters = {k: args[k] for k in parameter_names}

            np.random.seed(0) # make sort-of deterministic...

            f(**parameters)

            ax = fig.axes()[-1]
        
            if '_caption' in args and args['_caption'] != "":
                caption = args['_caption'] 
                at = AnchoredText(caption, 
                                  loc='upper center', 
                                  prop=dict(size=16), 
                                  frameon=True)
                at.set_zorder(60)
                ax.add_artist(at)
                at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2")
                at.patch.set_facecolor('yellow')

            if show_params:
                if hasattr(f, '__name__'):
                    name = f.__name__
                else:
                    name = f.func.__name__
                    parameters['...'] = '...'

                def r(v):
                    if isinstance(v, numbers.Number):
                        s = str(round(v, 4))
                    elif isinstance(v, (str, bool)):
                        s = repr(v)
                    elif issubclass(type(v), object):
                        s = '...'
                    elif callable(v):
                        if hasattr(v, '__name__'):
                            s = v.__name__
                        else:
                            s = repr(v)
                    else:
                        s = repr(v)
                    if len(s) > 16:
                        s = s[0:13] + '...'
                    return s
                    

                arg_values = f"{name}({' ' * (50 - len(name))}\n  "  \
                            + f",\n  ".join([ f"{key} = {r(parameters[key])}" for key in parameter_names if not key.startswith("_") ]) \
                            + "\n)"
                at = AnchoredText(arg_values,
                                loc='upper left', 
                                prop=dict(size=10,fontfamily='sans-serif'), 
                                frameon=True,
                                bbox_to_anchor=(1.025, 0.75),
                                bbox_transform=ax.transAxes)
                ax.add_artist(at)
                at.patch.set_boxstyle("round,pad=0.,rounding_size=0.2") 
                at.patch.set_facecolor('wheat')
        
            buf = io.BytesIO()
            plt.savefig(buf, format='png')  # Save as PNG
            buf.seek(0)  # Move to the beginning of the buffer
            
            # Encode the buffer to base64
            img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
            return "data:image/png;base64," + img_base64

    if show_params:
        fig.fig.tight_layout(pad=2, rect=[0, 0, 0.75, 1])
    else: 
        fig.fig.tight_layout(pad=2)
        
    base64s = [ one_frame(args) for args in gen() ]

    return base64s

    # if show_params:
    #     fig.fig.tight_layout(pad=2, rect=[0, 0, 0.75, 1])
    # else: 
    #     fig.fig.tight_layout(pad=2
    #                          )
    # video = anim.to_jshtml(default_mode=default_mode)
        
    # plots.close(fig.fig)
    # display(HTML(video))


# In[7]:


""" <div class="lm-Widget p-Widget jp-OutputArea jp-Cell-outputArea fake" style="">
        <div class="lm-Widget p-Widget lm-Panel p-Panel jp-OutputArea-child">
            <div class="lm-Widget p-Widget jp-OutputPrompt jp-OutputArea-prompt"></div>
            <div class="lm-Widget p-Widget lm-Panel p-Panel jupyter-widgets jp-OutputArea-output">
                <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-slider widget-hslider">
                    <label class="widget-label" title="UniqueDescription" style="">UniqueDescription</label>
                    <div class="slider-container">
                        <input type="range" class="ui-slider ui-corner-all ui-widget ui-widget-content slider ui-slider-horizontal"  id="slider_{uid}" min="0" max="{len(images)-1}" value="0">                
                    </div>
                    <div class="widget-readout" contenteditable="true" style="" id="sliderValue_{uid}">8</div>
                </div>
                <img id="dynamicImage_{uid}" src="{images[0]}" alt="Dynamic Image" style="display: inline;">
            </div>
        </div>
    </div>
    
"""    


# In[8]:


def visualize_distributions(N, sample_size, num_trials):
    """A single function to run our simulation for a given N, sample_size, and num_trials."""
    population = np.arange(1, N+1)
    
    # Builds up our outcomes table one row at a time.  We do this to ensure
    # we can apply both statistics to the same samples.
    outcomes_table = Table(["Max", "2*Mean"])
    
    for i in np.arange(num_trials):
        sample = np.random.choice(population, sample_size)
        outcomes_table.append(make_array(max(sample), 2 * np.mean(sample)))
        
    outcomes_table.hist(bins=np.arange(1, 2 * N, 10),
                        xlim=(0,800),
                        ylim=(0,0.1),
                        xlabel='Predicted N',
                        title='Snoopy Fleet')

def gen():
    N, sample_size, num_trials = 400, 10, 0
    for i in np.arange(1,10,2):
        num_trials = i
        yield locals()
    
images = animate(visualize_distributions, gen)


# In[9]:


import matplotlib.pyplot as plt
import io
import numpy as np
import base64
from IPython.display import display, HTML
import uuid

def make_slider(images):
    uid = uuid.uuid4().int  # Generates a random UUID.
    html = f"""
    <style>
      .slider-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 10px;  /* added space between slider and image */
      }}
      .value-label {{
        margin-left: 10px;
        width: 40px; /* fixed width */
        display: inline-block; /* makes width effective */
        text-align: right; /* aligns the number to the right */
      }}
      .fake {{
        font-family: var(--jp-ui-font-family);
        margin: 0;
        padding: 0;
        overflow: hidden;      
      }}
    </style>
    
    <div class="lm-Widget p-Widget lm-Panel p-Panel jp-Cell-outputWrapper">
        <div class="lm-Widget p-Widget jp-OutputArea jp-Cell-outputArea" style="">
            <div class="lm-Widget p-Widget lm-Panel p-Panel jp-OutputArea-child">
                <div class="lm-Widget p-Widget jp-OutputPrompt jp-OutputArea-prompt"></div>
                <div class="lm-Widget p-Widget lm-Panel p-Panel jupyter-widgets jp-OutputArea-output">
                    <div class="lm-Widget p-Widget jupyter-widgets widget-inline-hbox widget-slider widget-hslider"><label
                            class="widget-label" title="Test:" style="">Test:</label>
                        <div class="slider-container">
                            <input type="range" class="ui-slider ui-corner-all ui-widget ui-widget-content slider ui-slider-horizontal"  id="slider_{uid}" min="0" max="{len(images)-1}" value="0">                
                        </div>
                        <div class="widget-readout" contenteditable="true" style="" id="sliderValue_{uid}">7</div>
                    </div>
                    <img id="dynamicImage_{uid}" src="{images[0]}" alt="Dynamic Image" width="500px" style="display: inline;">
                </div>
            </div>
        </div>
    </div>
        
    <script>
      var _slider_{uid} = document.getElementById('slider_{uid}');
      var _sliderValue_{uid} = document.getElementById('sliderValue_{uid}');
      var _dynamicImage_{uid} = document.getElementById('dynamicImage_{uid}');
    
      var images = [ 
        {",".join([ '"' + x + '"' for x in images])}
      ]
    
      _slider_{uid}.oninput = function() {{
        _sliderValue_{uid}.textContent = this.value;
        _dynamicImage_{uid}.src = images[this.value];
      }}
    </script>
    """
    return html



    # <div class="slider-container">
    #   <label for="slider_{uid}">Adjust Value:</label>
    #   <input type="range" id="slider_{uid}" min="0" max="{len(images)-1}" value="0">
    #   <span class="value-label" id="sliderValue_{uid}">0</span>
    # </div>
    # <img id="dynamicImage_{uid}" src="{images[0]}" alt="Dynamic Image">


html = make_slider(images)
display(HTML(html))


# In[10]:


from IPython.display import *


# In[11]:


t = Table().with_columns("A", [1,2,3], "B", [2,3,4])
t._repr_html_()


# In[12]:


f = Figure()


# In[17]:


vars(f)


# In[18]:


vars(Figure)


# In[15]:


vars(str)


# In[ ]:


var _slider_{uid} = document.getElementById('slider_{uid}');
var _sliderValue_{uid} = document.getElementById('sliderValue_{uid}');
var _dynamicImage_{uid} = document.getElementById('dynamicImage_{uid}');

// Function to load images array asynchronously
function loadImages() {
  return fetch('images_{uid}.json')  // Adjust the file path as necessary
    .then(response => response.json())
    .then(data => {
      return data;  // Assuming the JSON file contains the array directly
    })
    .catch(error => {
      console.error('Failed to load images:', error);
    });
}

// Load images and then set up the slider functionality
loadImages().then(images => {
  if (images) {
    _slider_{uid}.oninput = function() {
      _sliderValue_{uid}.textContent = this.value;
      _dynamicImage_{uid}.src = images[this.value];
    };
  } else {
    console.error('No images loaded');
  }
});


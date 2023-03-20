"""
CS 104 code that can be resused for statistical inference such as bootstrapping 
and linear regression.

1. Bootstrap.  

    You will typically need to implement your own bootstrapping
    function, such as in the notebooks for our Bootstrapping and
    Confidence Interval lectures.  We provide here the
   
        percentile_method(ci_percent, statistics)
   
    function for computing confidence intervals.
   
2. Linear Regression.

    The most important function for linear regressions is the function
     
         linear_regression(table, x_label, y_label)

    that returns an array containing the slope and intercept of the line 
    best fitting  the table's data according to the mean square error loss 
    function.  We also provide several diagnostic functions to help you
    determine the strength of correlation quality of the fit.  The first
    two are numeric.  The last two are visual.
    
        pearson_correlation(table, x_label, y_label)
        r2_score(table, x_label, y_label, a, b)
        plot_scatter_with_line(table, x_label, y_label, a, b)
        plot_residuals(table, x_label, y_label, a, b)

    The most typical use case is to first call linear_regression to get the
    regression line, and then inspect its quality numerically and visually.
    
"""

# __all__ = [ 'linear_regression' ]

from datascience import *
import numpy as np
import matplotlib.pyplot as plots
import matplotlib.colors as colors

def make_simulated_statistics(make_one_sample, sample_size,
                              compute_sample_statistic, num_samples):
    simulated_statistics = make_array()
    for i in np.arange(0, num_samples):
        simulated_sample = make_one_sample(sample_size)
        sample_statistic = compute_sample_statistic(simulated_sample)
        simulated_statistics = np.append(simulated_statistics, sample_statistic)
    return simulated_statistics

def visualize_simulated_statistics(simulated_statistics, observed_statistic = None, model_parameter = None):
    table = Table().with_columns("Simulated Statistics", simulated_statistics)
    plot = table.hist("Simulated Statistics",
                     title="Simulated Statistics")
    if observed_statistic is not None:
        plot.dot(observed_statistic)
    if model_parameter is not None:
        plot.square(model_parameter)
    return plot

def calculate_pvalue(simulated_statistics, observed_statistic): 
    """
    Return the proportion of the simulated statistics that are greater than 
    or equal to the observed statistic
    """
    return np.count_nonzero(simulated_statistics >= observed_statistic) / len(simulated_statistics)

def visualize_difference_from_model(statistics, observed_statistic = None, model_parameter = None, p_cutoff = None):
    differences = abs(statistics - model_parameter)
    np.sort(differences)
    table = Table().with_columns("abs(sample statistic - model parameter)", differences)
    
    if p_cutoff != None:
        left_end = percentile(100 - p_cutoff, differences)
    else:    
        left_end = None
    
    plot = table.hist("abs(sample statistic - model parameter)",
                      title="Differences from Model Parameter",
                      left_end = left_end)
    if observed_statistic is not None:
        plot.dot(abs(observed_statistic - model_parameter)) 
    return plot

def total_variation_distance(distribution1, distribution2):
    return sum(np.abs(distribution1 - distribution2)) / 2

def permutation_sample(table, group_column_name):
    """
    Returns: The table with a new "Shuffled Label" column containing
    the shuffled values of the group column.
    """
    
    # array of shuffled labels
    shuffled_labels = table.sample(with_replacement=False).column(group_column_name)
    
    # table of numerical variable and shuffled labels
    shuffled_table = table.with_column('Shuffled Label', shuffled_labels)
    
    return shuffled_table

def bootstrap(observed_sample, num_trials, resample_statistic): 

    bootstrap_statistics = make_array()
    
    for i in np.arange(0, num_trials): 
        #Key: in bootstrapping we must always sample with replacement 
        simulated_resample = boston_sample.sample()
        
        resample_statistic = percentile(50, simulated_resample.column('REGULAR')) #get the median for that one resample 
        bootstrap_statistics = np.append(bootstrap_statistics, resample_statistic)
    
    return bootstrap_statistics

######################################################################
# Bootstrapping: generic code that can be resued 
######################################################################

def percentile_method(ci_percent, bootstrap_statistics):
    """
    Return an array with the lower and upper bound of the ci_percent confidence interval.
    """
    # percent in each of the the left/right tails
    percent_in_each_tail = (100 - ci_percent) / 2   
    left = percentile(percent_in_each_tail, bootstrap_statistics)
    right = percentile(100 - percent_in_each_tail, bootstrap_statistics)
    return make_array(left, right)

def visualize_ci(ci_percent, bootstrap_statistics):
    results = Table().with_column('Bootstrap Samples Percent Purple', bootstrap_statistics)
    
    mendel_plot("Mendel's garden A", observed_statistic, bootstrap_statistics)

    left,right = left_right = percentile_method(ci_percent, bootstrap_statistics)
    plots.plot(left_right, [0, 0], color='yellow', lw=8)
    

######################################################################
# Linear regression: generic code that can be resued 
######################################################################

def pearson_correlation(table, x_label, y_label):
    """
    Return the correlation coefficient capturing the sign
    and strength of the association between the given columns in the
    table.
    """
    x = table.column(x_label)
    y = table.column(y_label)
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    numerator = sum((x - x_mean) * (y - y_mean)) 
    denominator = np.sqrt(sum((x - x_mean)**2)) * np.sqrt(sum((y - y_mean)**2))
    return numerator / denominator 

# def plot_line(a, b, x): 
#     """
#     Plots a line using the give slope and intercept over the
#     range of x-values in the x array.
#     """
#     xlims = make_array(min(x), max(x))
#     plots.plot(xlims, a * xlims + b, lw=4)
    
def line_predictions(a, b, x): 
    """
    Computes the prediction  y_hat = a * x + b
    where a and b are the slope and intercept and x is the set of x-values.
    """
    return a * x + b

def mean_squared_error(table, x_label, y_label, a, b): 
    """
    Returns the mean squared error for the line described by slope a and
    intercept b when used to fit the data in the tables x_label and y_label
    columns.
    """
    y_hat = line_predictions(a, b, table.column(x_label))
    residual = table.column(y_label) - y_hat
    return np.mean(residual**2)

def linear_regression(table, x_label, y_label):
    """
    Return an array containing the slope and intercept of the line best fitting 
    the table's data according to the mean square error loss function.  Example:
    
    optimal = linear_regression(fortis, 'Beak length, mm', 'Beak depth, mm') 
    a = optimal.item(0)
    b = optimal.item(1)    
    
    OR
    
    a,b = linear_regression(fortis, 'Beak length, mm', 'Beak depth, mm') 
    """
    
    # A helper function that takes *only* the two variables we need to optimize.
    # This is necessary to use minimize below, because the function we want
    # to minimize cannot take any parameters beyond those it will solve for.
    def mse_for_a_b(a, b):
        return mean_squared_error(table, x_label, y_label, a, b)
    
    # We can use a built-in function `minimize` that uses gradiant descent
    # to find the optimal a and b for our mean squared error function 
    return minimize(mse_for_a_b)

def calculate_residuals(table, x_label, y_label, a, b): 
    """
    Residuals = y - y_hat 
    where y_hat are the predictions from the line characterized by 
    y = ax+b
    """ 
    x = table.column(x_label)
    y = table.column(y_label)
    y_hat = line_predictions(a, b, x)
    residual = y - y_hat
    return residual

def r2_score(table, x_label, y_label, a, b):
    """
    R-squared score (also called the "coefficient of determination")
    for the predictions given y=ax+b
    """ 
    residual = calculate_residuals(table, x_label, y_label, a, b)
    numerator = sum(residual**2)
    y = table.column(y_label)
    y_mean = np.mean(y)
    denominator = sum((y-y_mean)**2)
    return 1 - numerator/denominator

######################################################################
# Plotting: this code can be reused to plot aspects of linear regression
######################################################################

def plot_scatter_with_line(table, x_label, y_label, a, b):
    """
    Draw a scatter plot of the given table data overlaid with
    a line having the given slope a and intercept b.
    """
    x = table.column(x_label)
    xlims = make_array(min(x), max(x))
    y = table.column(y_label)
    ylims = make_array(min(y), max(y))
    plot = table.scatter(x_label, y_label,
                  title='a = ' + str(round(a,3)) + '; b = ' + str(round(b,3)))
    plot.line(xlims, a * xlims + b, lw=4,color="C0"),
    


def plot_residuals(table, x_label, y_label, a, b):
    """
    Plots x-axis as the original x values 
    and the y-axis as the residuals of the predictions 

    Also plots the y=0 horizontal line 
    """ 
    x = table.column(x_label)
    residual = calculate_residuals(table, x_label, y_label, a, b)
    t = Table().with_columns(x_label, x, 'residuals', residual)
    plot = t.scatter(x_label, 'residuals', color='red', 
              title='Residual Plot')
    plot.line(make_array(min(x), max(x)), make_array(0,0), color='darkblue', lw=4, path_effects=None)
    


######################################################################
# The following are more sophisticated plotting functions we used
# for lecture examples.  You may use them if you like, but do not
# worry about the details of the code.
######################################################################


def plot_regression_line_and_mse_heat(table, x_label, y_label, a, b, show_mse=None, a_space=None, b_space=None):
    """
    Left plot: the scatter plot with line y=ax+b
    Right plot: None, 2D heat map of MSE, or 3D surface plot of MSE 
    """
    if a_space is None: a_space = np.linspace(-10*a, 10*a, 200)
    if b_space is None: b_space = np.linspace(-10*b, 10*b, 200)
    a_space, b_space = np.meshgrid(a_space, b_space)
    broadcasted = np.broadcast(a_space, b_space)
    mses = np.empty(broadcasted.shape)
    mses.flat = [mean_squared_error(table, x_label, y_label, a, b) for (a,b) in broadcasted]
    
    fig, ax = plots.subplots(1,2,figsize=(12,6))
    
    #Plot the scatter plot and best fit line on the left
    with Plot(ax[0]):
        plot_scatter_with_line(table, x_label, y_label, a, b)

    if show_mse == '2d':
        with Plot(ax[1]):
            mse = mean_squared_error(table, x_label, y_label, a, b)
            ax[1].pcolormesh(a_space, b_space, mses, cmap='viridis', 
                             norm=colors.PowerNorm(gamma=0.25,
                                                   vmin=mses.min(), 
                                                   vmax=mses.max()));
            ax[1].scatter(a,b,s=100,color='red');
            ax[1].set_xlabel('a')
            ax[1].set_ylabel('b')
            ax[1].set_title('Mean Squared Error: ' + str(np.round(mse, 3)))

    elif show_mse == "3d": 
        ax[1] = plots.subplot(1, 2, 2, projection='3d')
        with Plot(ax[1]):
            ax[1].plot_surface(a_space, b_space, mses,
                            cmap='viridis', 
                            antialiased=False, 
                            linewidth=0,
                            norm = colors.PowerNorm(gamma=0.25,vmin=mses.min(), vmax=mses.max()))

            ax[1].plot([a],[b],[mean_squared_error(table, x_label, y_label, a, b)], 'ro',zorder=3);
            ax[1].set_xlabel('a')
            ax[1].set_ylabel('b')
            ax[1].set_title('Mean Squared Error')
    
    
def plot_regression_line_and_residuals(table, x_label, y_label, a, b):
    """
    Left plot: a scatter plot and line for the provided table and slope/intercept
    Right plot: The residuals of the predictions.
    """
    
    fig, ax = plots.subplots(1,2,figsize=(12,6))
    
    #Plot the scatter plot and best fit line on the left
    with Plot(ax[0]):
        plot_scatter_with_line(table, x_label, y_label, a, b)
    
    with Plot(ax[1]):
        plot_residuals(table, x_label, y_label, a, b)
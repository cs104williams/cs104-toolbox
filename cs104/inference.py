"""
CS 104 code that can be reused for statistical inference such as bootstrapping 
and linear regression.

See the following for documentation:

https://cs104williams.github.io/assets/inference-library-ref.html

"""

# __all__ = [ 'linear_regression' ]

from datascience import *
import numpy as np
import matplotlib.pyplot as plots
import matplotlib.colors as colors

from .docs import doc_tag

###

@doc_tag(path='inference-library-ref.html')
def simulate(make_one_outcome, num_trials):
    """
    Return an array of num_trials values, each 
    of which was created by calling make_one_outcome().
    """
    outcomes = make_array()
    for i in np.arange(0, num_trials):
        outcome = make_one_outcome()
        outcomes = np.append(outcomes, outcome)

    return outcomes

# @doc_tag(path='inference-library-ref.html')
# def array_hist(values, **kwargs):
#     """
#     Create a histogram for the numerical data in values.
#     Returns the Plot object for the histogram.
#     """
#     label = "Values"
#     table = Table().with_columns(label, values)
    
#     plot = table.hist(label, **kwargs)
#     return plot

@doc_tag(path='inference-library-ref.html')
def simulate_sample_statistic(make_one_sample, sample_size,
                              compute_sample_statistic, num_trials):
    """
    Simulates `num_trials` sampling steps and returns an array of the
    statistic for those samples.  The parameters are:

    * make_one_sample: a function that takes an integer n and returns a 
                       sample as an array of n elements.
    
    * sample_size: the size of the samples to use in the simulation.
    
    * compute_statistic: a function that takes a sample as 
                         an array and returns the statistic for that sample. 
    
    * num_trials: the number of simulation steps to perform.
    """

    simulated_statistics = make_array()
    for i in np.arange(0, num_trials):
        simulated_sample = make_one_sample(sample_size)
        sample_statistic = compute_sample_statistic(simulated_sample)
        simulated_statistics = np.append(simulated_statistics, sample_statistic)
    return simulated_statistics

@doc_tag(path='inference-library-ref.html')
def empirical_pvalue(null_statistics, observed_statistic): 
    """
    Return the proportion of the null statistics that are greater than 
    or equal to the observed statistic.
    """
    return np.count_nonzero(null_statistics >= observed_statistic) / len(null_statistics)


###        
        
@doc_tag(path='inference-library-ref.html')
def permutation_sample(table, group_label):
    """
    Takes a table and the label of a column used to group rows.
    Returns a copy of the table with a new "Shuffled Label" column
    containing the shuffled values from the group column.
    """
    
    # array of shuffled labels
    shuffled_labels = table.sample(with_replacement=False).column(group_label)
    
    # table of numerical variable and shuffled labels
    shuffled_table = table.with_column('Shuffled Label', shuffled_labels)
    
    return shuffled_table


def abs_difference_of_means(table, group_label, value_label):
    """
    Takes a table, the label of the column used to divide rows into
    two groups, and the label of the column storing the values
    for each row.
    Returns the absolute difference of the mean 
    value for the two groups.
    """
    
    # table containing group means
    means_table = table.group(group_label, np.mean)
    
    # array of group means
    means = means_table.column(value_label + ' mean')
    
    return abs(means.item(0) - means.item(1))



@doc_tag(path='inference-library-ref.html')
def simulate_permutation_statistic(table, group_label, value_label, 
                                   num_trials):
    """
    Simulates `num_trials` sampling steps and returns an array of the
    `abs_difference_of_means` statistic for those samples.  

    The parameters are:

    * table:       the Table to which we'll apply a permutation test.
    
    * group_label: the label of a column used to divide the rows into two groups.
    
    * value_label: the label of the column storing the values
                   for each row.  This column should contain numerical
                   values.  The values are restricted to 0 and 1, we can
                   interpret the sample statistic as being the absolute 
                   difference in the proportion of 1's in the two groups.
    
    * num_trials:  the number of permutations to compute.
    """

    sample_statistics = make_array()
    for i in np.arange(num_trials):
        one_sample = permutation_sample(table, group_label)
        sample_statistic = abs_difference_of_means(one_sample, "Shuffled Label", value_label)
        sample_statistics = np.append(sample_statistics, sample_statistic)
    return sample_statistics


######################################################################
# Bootstrapping: generic code that can be resued 
######################################################################

@doc_tag(path='inference-library-ref.html')
def confidence_interval(ci_percent, bootstrap_statistics):
    """
    Return an array with the lower and upper bound of the ci_percent confidence interval.
    """
    # percent in each of the the left/right tails
    percent_in_each_tail = (100 - ci_percent) / 2   
    left = percentile(percent_in_each_tail, bootstrap_statistics)
    right = percentile(100 - percent_in_each_tail, bootstrap_statistics)
    return make_array(left, right)

@doc_tag(path='inference-library-ref.html')
def bootstrap(initial_sample, compute_statistic, num_trials): 
    """
    Creates num_trials resamples of the initial sample.
    Returns an array of the provided statistic for those samples.

    * initial_sample: the initial sample, as an array.
    
    * compute_statistic: a function that takes a sample as 
                         an array and returns the statistic for that sample. 
    
    * num_trials: the number of bootstrap samples to create.

    """
    statistics = make_array()
    
    for i in np.arange(0, num_trials): 
        #Key: in bootstrapping we must always sample with replacement 
        simulated_resample = initial_sample.sample()
        
        resample_statistic = compute_statistic(simulated_resample)
        statistics = np.append(statistics, resample_statistic)
    
    return statistics

######################################################################
# Linear regression: generic code that can be resued 
######################################################################

@doc_tag(path='inference-library-ref.html')
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
    
@doc_tag(path='inference-library-ref.html')
def line_predictions(a, b, x): 
    """
    Computes the prediction  y_hat = a * x + b
    where a and b are the slope and intercept and x is the set of x-values.
    """
    return a * x + b

@doc_tag(path='inference-library-ref.html')
def mean_squared_error(table, x_label, y_label, a, b): 
    """
    Returns the mean squared error for the line described by slope a and
    intercept b when used to fit the data in the tables x_label and y_label
    columns.
    """
    y_hat = line_predictions(a, b, table.column(x_label))
    residual = table.column(y_label) - y_hat
    return np.mean(residual**2)

@doc_tag(path='inference-library-ref.html')
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

@doc_tag(path='inference-library-ref.html')
def residuals(table, x_label, y_label, a, b): 
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

@doc_tag(path='inference-library-ref.html')
def r2_score(table, x_label, y_label, a, b):
    """
    R-squared score (also called the "coefficient of determination")
    for the predictions given y=ax+b
    """ 
    residual = residuals(table, x_label, y_label, a, b)
    numerator = sum(residual**2)
    y = table.column(y_label)
    y_mean = np.mean(y)
    denominator = sum((y-y_mean)**2)
    return 1 - numerator/denominator

######################################################################
# Plotting: this code can be reused to plot aspects of linear regression
######################################################################

@doc_tag(path='inference-library-ref.html')
def plot_scatter_with_line(table, x_label, y_label, a, b):
    """
    Draw a scatter plot of the given table data overlaid with
    a line having the given slope a and intercept b.
    """
    plot = table.scatter(x_label, y_label, title='a = ' + str(round(a,3)) + '; b = ' + str(round(b,3)))
    plot.line(slope=a, intercept=b, lw=2, color="C0")
    return plot
    


@doc_tag(path='inference-library-ref.html')
def plot_residuals(table, x_label, y_label, a, b):
    """
    Plots x-axis as the original x values 
    and the y-axis as the residuals of the predictions 

    Also plots the y=0 horizontal line 
    """ 
    x = table.column(x_label)
    residual = residuals(table, x_label, y_label, a, b)
    largest_residual = abs(max(residual))
    residual_table = Table().with_columns(x_label, x, 'residuals', residual)
    plot = residual_table.scatter(x_label, 'residuals',
                                  color='red', 
                                  title='Residual Plot',
                                  ylim=1.05 * make_array(-largest_residual, largest_residual))
    plot.line(y = 0, color='darkblue', lw=2)
    return plot
    

def plot_full_regression(table, x_label, y_label, a, b):
    """
    Left plot: a scatter plot and line for the provided table and slope/intercept
    Right plot: The residuals of the predictions.
    """
    
    with Figure(1,2):
        plot_scatter_with_line(table, x_label, y_label, a, b)
        plot_residuals(table, x_label, y_label, a, b)
    

######################################################################
# The following are more sophisticated plotting functions we used
# for lecture examples.  You may use them if you like, but do not
# worry about the details of the code.
######################################################################


def plot_regression_line_and_mse_heat(table, x_label, y_label, a, b, show_mse=None, a_space=None, b_space=None, _fig=None):
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
        
    if _fig is None:
        _fig = Figure(1,2)
        
    ax = _fig.axes()

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
    
    
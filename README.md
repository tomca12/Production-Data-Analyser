# Production-Data-Analyser
This program is designed to visualise data (typically measurements of production as  recorded by LC/MS, GC/MS, HPLC or other detection methods) in the form of bar plots. The program takes an input file with data and optionally a standard that converts the raw data to concentrations.  Concentrations can also be given directly. Regression lines can be plotted for standard.  The program enables creating and exporting visually pleasing graphs with multiple bars for each sample (defined as 'methods' in the experimental sense),  with error bars, and each method can have its own standard. Many graph parameters can be set custom and the program allows the creation of bar plots with a table in place of the x-axis labels (frequently used for synoptical visualisation of sample differences).  Additionally, paired or independent t-tests can be calculated on the data and the visualisation of significance is shown in the graph as asterisks.   
Author: Lucie Studena

## Data Input Format
The typical input format of the data is a .csv file with following essential columns: 
- name
- area
- method
-fix

The **name** column identifies the sample. If more samples have the same name, they are grouped together as measurements of the same population for statistical analysis and for graphing

The **area** column specifies the raw value measured. If a standard is provided later, a concentration is calculated using the standard. 

The **method** column specifies the experimental method. In case more than one method is contained in the file, each method will be plotted as a different-colour plot. Samples of the same *name* and different *method* are treated as separate populations for statistical analysis.

Tha **fix** column may remain empty but is used in case some values need adjusting - for example input 'ignore' would treat the row as non-existent in the final statistical calculations and plotting.


Forthermore, several optional columns may be used: 
- concentration
- group

The column **concentration** allows giving concentrations directly, without providing the raw values

The column **group** allows several samples with a different name but the same group to be grouped together as one population for statistical analysis if this is specified in the statistical function used. 



## To Create the Object: 
The object is creted as an `MSData` object with a single essential argument, `'data_csv'`, containing the input data. Optional arguments are `names_all='names_all.txt'` and `concentration_units=None`

## Available Functions
Numerous functions can then be performed on the data object to visualise the data and perform statistical calculations. 

### use_standard
`MSData.use_standard(standard_csv, method=None)`

Optionally apply standard to the data. It will calculate the product concentration. Subsequently used functions will then use the calculated concentration data.
        
##### Parameters:
`standard_csv` - input csv data from standard  
`method=None` - allows using different standards for different methods - eg. in the original samples, there would be different standards for a final product and the chemical intermediate and they would be plotted as different bars  

### calculate_plot_data
`MSData.calculate_plot_data(names, methods)`

Calculates the averages and standard deviations of the replicates to plot. If OD (optical density) values are provided, this also calculates the values per OD

### plot_regression
`MSData.plot_regression(savefile=None)`

Only use this function if using a standard. It provides a scatter plot with the regression line to check the quality of the standard and regression

##### Parameters:
`savefile=None` - input a file name in the .png format to save the figure

### make_barplot
`MSData.make_barplot(names_txt=None,
              output_name=None,
              title=None, 
              per_OD=False, 
              remove_blank=None, 
              ylabel=None, 
              fig_height=None, 
              fig_width=None, 
              palette='muted', 
              plot_data_exp=None,
              ylim_max=None,
draw_legend=True)`

Function that generates a barplot from the calcualted plot data (only use after calculate_plot_data function)

##### Parameters:
`names_txt=None` - can plot only some samples or change the order of samples - format is a text file with each name as a row or a list with sample names  
`output_name=None` - name for saving the barplot, typically with .png format  
`title=None` - specifies the graph title  
`per_OD=False` - is True if the graph should have the concentrations normalised per measured optical density ('OD', must be specified as an column in the input file)  
`remove_blank=None` - if True, will ignore all samples that have 'blank' in the name. Used by default if per_OD is True as otherwise the graphs look distorted for blanks  
`ylabel=None` - specifies the y asix label  
`fig_height=None` - specifies the saved figure height  
`fig_width=None` - specifies saved figure width  
`palette='muted'` - allows choosing from pre-defined Seaborn palettes by their Seaborn names  
`plot_data_exp=None` -  name for export of the the plot data table for thegraph as csv  
`ylim_max=None` - changes the maximum value shown on y axis. Especially useful if visualising significance as asterisks as they are usually too close to the edge of the graph by default  
`draw_legend=True` - if False, no legend will be drawn  

### make_barplot_table
`MSData.make_barplot_table(tableData, 
                           output_name=None, 
                           title=None, 
                           per_OD=False, 
                           remove_blank=None, 
                           ylabel=None, 
                           fig_height=None, 
                           fig_width=None, 
                           palette='muted', 
                           plot_data_exp=None, 
                           ylim_max=None,
                           draw_legend=True)`

Function that builds on top of the make_barplot function. It allows to use a table instead of sample names (can be used for describing each sample by genes modified, etc.). It generates a barplot from the calcualted plot data and uses most the same parameters as make_barplot function.

##### Parameters:
`tableData` - required parameter - a csv file that specifies that should be in the x axis description table. First row is the list of sample names. Only samples appearing in the table will be displayed.   
`output_name=None` - name for saving the barplot, typically with .png format  
`title=None` - specifies the graph title  
`per_OD=False` - is True if the graph should have the concentrations normalised per measured optical density ('OD', must be specified as an column in the input file)  
`remove_blank=None` - if True, will ignore all samples that have 'blank' in the name. Used by default if per_OD is True as otherwise the graphs look distorted for blanks  
`ylabel=None` - specifies the y asix label  
`fig_height=None` - specifies the saved figure height  
`fig_width=None` - specifies saved figure width  
`palette='muted'` - allows choosing from pre-defined Seaborn palettes by their Seaborn names  
`plot_data_exp=None` -  name for export of the the plot data table for thegraph as csv  
`ylim_max=None` - changes the maximum value shown on y axis. Especially useful if visualising significance as asterisks as they are usually too close to the edge of the graph by default  
`draw_legend=True` - if False, no legend will be drawn  

       
### make_barplot_sns
`MSData.make_barplot_sns(output_name, names_txt=None)`  

A method that makes simpler similar graphs using Seaborn. In some cases, it is smoother and looks nicer but offers less flexibility

##### Parameters:
`output_name` - specifies the output file name, usually in .png  
`names_txt=None` - a lost of text file with names, analogous to make_barplot  
 
### export_dataframe
`MSData.export_dataframe(filename)`

Export the data frame used for the figures using the `filename` input as the file name.


### ttest_be_method_paired
`MSData.ttest_by_method_paired(file_paired=None, methods=None)`

Method still in development. It gives paired t-test results as a csv table file where for each sample, two methods are compared. Should work seamlessly for two methods and now also for more methods provided, if the methods are specified as a list of indexes in the self.methods. Otherwise, it does just the first two methods. Note that for paired t-test, both methods to be compared must have the same number of measurements.

##### Parameters:
`file_paired=None` - file name (in csv) for saving the results  
`methods=None` - if None, first two methods are compared. If a list of indexes is specified, those are compared"""
 
### ttest_independent
`MSData.ttest_independent(method = 'all', sample_names='all_names', file_ind=None, group_by=False)`

Method still in development. It will take a list of sample names and compare all of them against each other. This is slightly inefficient because each calculation is done twice (hence in development) but still very quick and enough for the purposes used. 

##### Parameters:
method='all' - specifies which methods should be compared (if only some of interest) can be a string of a specific method or the word 'all'  
sample_names='all_names' - specifies just some samples to compare or all (default)  
file_ind=None - name of the csv file to save the results  
group-by=False - if True, takes the column which indicates which samples are in fact the same (eg. just different clones) and so should be grouped for the purposes of statistics, not compared against each other or other samples separately. Groups need to be specified as a column of the input file  
  
### annot_stat
`annot_stat(self, star, x1, x2, y, h, col='k')`

Plots a graphic representation of the significance (usually stars)

##### Parameters
`star` - text to be written, usually different amount of asterisks  
`x1` - lower x position of the 'leg'  
`x2` - higher x position of the 'leg'  
`y` - y position of the bar  
`h` - height of the bar above the 'legs'  
`col=k` - specifies the colour  

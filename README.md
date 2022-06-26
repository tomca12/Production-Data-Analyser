# Production-Data-Analyser
This program is designed to visualise data (typically measurements of production as  recorded by LC/MS, GC/MS, HPLC or other detection methods) in the form of bar plots. The program takes an input file with data and optionally a standard that converts the raw data to concentrations.  Concentrations can also be given directly. Regression lines can be plotted for standard.  The program enables creating and exporting visually pleasing graphs with multiple bars for each sample (defined as 'methods' in the experimental sense),  with error bars, and each method can have its own standard. Many graph parameters can be set custom and the program allows the creation of bar plots with a table in place of the x-axis labels (frequently used for synoptical visualisation of sample differences).  Additionally, paired or independent t-tests can be calculated on the data and the visualisation of significance is shown in the graph as asterisks.   
Author: Lucie Studena

### Data Input Format
The typical input format of the data is a .csv file with following essential columns: 
- name
- area
- method
- fix

The **name** column identifies the sample. If more samples have the same name, they are grouped together as measurements of the same population for statistical analysis and for graphing

The **area** column specifies the raw value measured. If a standard is provided later, a concentration is calculated using the standard. 

The **method** column specifies the experimental method. In case more than one method is contained in the file, each method will be plotted as a different-colour plot. Samples of the same *name* and different *method* are treated as separate populations for statistical analysis.

Tha **fix** column may remain empty but is used in case some values need adjusting - for example input 'ignore' would treat the row as non-existent in the final statistical calculations and plotting.


Forthermore, several optional columns may be used: 
- concentration
- group

The column **concentration** allows giving concentrations directly, without providing the raw values

The column **group** allows several samples with a different name but the same group to be grouped together as one population for statistical analysis if this is specified in the statistical function used. 



### To Create the Object: 
The object is creted as an `MSData` object with a single essential argument, `'data_csv'`, containing the input data. Optional arguments are `names_all='names_all.txt'` and `concentration_units=None`

### Available Functions
Numerous functions can then be performed on the data object to visualise the data and perform statistical calculations. 

#### use_standard
`MSData.use_standard(standard_csv, method=None)`

Optionally apply standard to the data. It will calculate the product concentration. Subsequently used functions will then use the calculated concentration data.
        
###### Parameters:
`standard_csv` - input csv data from standard
`method=None` - allows using different standards for different methods - eg. in the original samples, there would be different standards for a final product and the chemical intermediate and they would be plotted as different bars

#### calculate_plot_data
`MSData.calculate_plot_data(names, methods)`

Calculates the averages and standard deviations of the replicates to plot. If OD (optical density) values are provided, this also calculates the values per OD

#### plot_regression
`MSData.plot_regression(savefile=None)`

Only use this function if using a standard. It provides a scatter plot with the regression line to check the quality of the standard and regression

###### Parameters:
`savefile=None` - input a file name in the .png format to save the figure

#### make_barplot
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

`MSData.export_dataframe(filename)`

`MSData.ttest_by_method_paired(file_paired=None, methods=None)`

`MSData.ttest_independent(method = 'all', sample_names='all_names', file_ind=None, group_by=False)`

`annot_stat(self, star, x1, x2, y, h, col='k')`


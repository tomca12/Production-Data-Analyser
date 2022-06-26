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


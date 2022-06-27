
'''This program is designed to visualise data (typically measurements of production as 
recorded by LC/MS, GC/MS, HPLC or other detection methods) in the form of barplots.
The program takes an input file with data and optionally a standard that converts the raw data to concentrations. 
Concentrations can also be given directly. Regression lines can be plotted for standard. 
The program enables creating and exporting visually pleasing graphs with multiple bars for each sample (defined as 'methods' in experimental sense), 
error bars, and each method can have its own standard. Many graph parameters can be set custom and the program allows creating barplots with a table
in place of the x-axis labels (frequently used for synoptical visualisation of sample differences). 
Additionally, paired or independent t-tests can be calculated on the data and visualisation of the significance shown in the graph as asterisks. 

Author: Lucie Studena
'''

from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import ListedColormap
import scipy


class MSData:
    def __init__(self, data_csv, names_all='names_all.txt', concentration_units=None):
        '''Parameters:
        data_csv - data for analysis in csv. Typical columns 'name', 'area', 'method', 'fix', 
        optionally 'OD' (optical density), 'concentration' (if not calculated later)
        
        names_all - file for all names
        concentration_units - can be specified custom if standard not used
        '''
        #read data from csv (data_csv input) to self..data
        self.data = pd.read_csv(data_csv, header=0)
        #recalculate optical density if dilution is provided
        if 'OD' in self.data and 'dilution' in self.data:
            self.data['OD']=self.data['OD']*self.data['dilution']
        #get list of unique sample names and write them to a file
        self.names = self.data.name.unique()
        with open(names_all, 'w') as f:
            for item in self.names:
                f.write(item+'\n')
                
        #get list of unique methods (meaning experimental methods here)
        self.methods = self.data.method.unique()    
        
        #ignore entries that have 'ignore' in the 'fix' column
        self.data = self.data[self.data['fix'] != 'ignore']
        
        #if 'fix' value is provided, use that instead (to not change the original data)
        for index, entry in self.data.iterrows():
            if pd.notna(entry['fix']):
                self.data['area'][index] = entry['fix']
        self.concentration_units = concentration_units
        self.export=[]

    #figure export function
    def __del__(self):
        for item in self.export:
            item['fig'].savefig(item['output_name'], dpi=300, bbox_inches='tight')

    def use_standard(self, standard_csv, method=None):
        '''Optionally apply standard to the data. It will calculate the product amounts. 
        Subsequently used functions will then use calculated concentration data.
        
        Parameters:
        standard_csv - input csv data fro standard
        method - allows using different standards for different methods - eg. in my samples, 
            I would have different standards for a final product and intermediate and plot them as different bars'''

        #read standard data
        self.standard = pd.read_csv(standard_csv, header=0)
        self.standard_y=self.standard.iloc[:,0].values.reshape(-1,1)
        self.standard_x=self.standard.iloc[:,1].values.reshape(-1,1)
        #initiate the model, fit data
        self.linear_regressor = LinearRegression()
        self.linear_regressor.fit(self.standard_x,self.standard_y)
        #predict y
        self.prediction_y = self.linear_regressor.predict(self.standard_x)
        #set units, convert to more conventional units
        self.concentration_units=self.standard.columns[0]
        if self.concentration_units == 'ug/ml':
            self.concentration_units = 'mg/L'              
            
        #print just for checking 
        print(self.linear_regressor.coef_)
        print(self.linear_regressor.intercept_)
        
        #fill out dataframe data predicted by regression if standard same for all methods
        if method==None:
            #only fill out concentration if not provided in the original file, initiate as a float
            if 'concentration' not in self.data:
                self.data['concentration'] = 0.0            
            
            #fill out predicted values
            data_x = self.data.iloc[:,1].values.reshape(-1,1)
            data_x = self.linear_regressor.predict(data_x)
            self.data['concentration']=data_x
            
        #fill out data predicted by the regression just for a specific method
        else:
            #only fill out concentration if not provided in the original file, initiate as a float
            if 'concentration' not in self.data:
                self.data['concentration'] = 0.0
            
            #fill out data predicted by the model (linear regressor)
            for index, row in self.data.iterrows():
                if row['method'] == method:
                    data_x = self.linear_regressor.predict([[row[1]]])[0][0]
                    self.data.at[index, 'concentration'] = data_x
                     

        #negative concentration does not make sense and is an artefact of standard/measurement unpercision - turn to 0. 
        self.data.loc[self.data['concentration'] < 0, 'concentration'] = 0          

 
    
    def calculate_plot_data(self, names, methods):
        ''' It calculates the averages and standard deviations of the replicates to plot. If OD (optical density) values are provided, this also calculates the values per OD'''
        
        #initiate plot_data dataframe
        plot_data = pd.DataFrame(columns=['name','method','average','std'])
        
        #subsetting the records (replicates) for the same sample
        for name in names:
            subset = self.data[self.data['name'] == name]
            for method in methods:
                row = {'name':name,'method':method}
                subset2 = subset[subset['method'] == method]
                
                #using calculated concentration
                if 'concentration' in subset2:                  
                    column_to_use = 'concentration'
                #using raw data (called 'area' as primarily used for HPLC or GC/MS or LC/MS data)
                else:
                    column_to_use = 'area'                      
        
                #if there is no match for that name and method, fill out NaN
                if subset2.empty:
                    row['average'] = np.nan
                    row['std'] = np.nan
                
                #fill out the mean and standard deviation of samples matching that name and method
                else:
                    row['average'] = subset2[column_to_use].mean()
                    row['std'] = subset2[column_to_use].std()
                
                #if OD values are given, calculate the mean and standard deviation for those too
                if 'OD' in subset2:
                    row['average_value_per_OD'] = (subset2[column_to_use]/subset2['OD']).mean()
                    row['std_value_per_OD'] = (subset2[column_to_use]/subset2['OD']).std()    
                plot_data = plot_data.append(row, ignore_index=True)
        
                #if the average of samples is smaller than 0, it is an artefact of measurement/standardisation and is turned to 0
                plot_data.loc[plot_data.average < 0, 'average'] = 0

        
        return plot_data                
                
    
    def plot_regression(self, savefile=None):
        '''Only use if using standard. It provides a scatter plot with the regression line to check the quality of the standard and regression'''
        fig = plt.figure()
        ax = fig.subplots()
        #scatter plot of standard values
        ax.scatter(self.standard_x,self.standard_y)
        #plot regression line over the scatter plot
        ax.plot(self.standard_x,self.prediction_y, color='red')
        #save figure
        if savefile:
            fig.savefig(savefile, dpi=300, bbox_inches='tight')
        
    def make_barplot(self, names_txt=None, 
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
                     draw_legend=True):
        '''Function that generates a barplot from the calcualted plot data (only use after calculate_plot_data function)
        
        Parameters:
        names_txt - can plot only some samples or change the order of samples - format is a text file with each name as a row or a list with sample names
        output_name - name to saving the barplot, typically with .png format
        title - specifies the graph title
        per_OD - is True if I want a graph with concentrations normalised per measured optical density
        remove_blank - will ignore all samples that have 'blank' in the name
        ylabel - change the y asix label
        fig_height - changes saved figure height
        fig_width - changes saved figure width
        palette - allows choosing from pre-defined Seaborn palettes by their Seaborn names
        plot_data_exp -  exports the plot data table for thegraph as csv
        ylim_max - changes the maximum amount shown on y axis. Especially useful if visualising significance asterisks later as they are usually too close to the edge of the graph by default
        draw_legend - by default True, if False, no legend will be drawn
        '''
        #error when OD data not provided and requesting an OD graph
        if per_OD == True and 'OD' not in self.data:
            print('ERROR: OD values not provided for a graph requiring per_OD measurement')     
            return
        
        #for per_OD graphs, remove blanks automatically as the graphs look confusing with them
        if remove_blank == None:
            remove_blank = per_OD 
                        
        #if no names parameter is provided, names are taken from the init function 
        if names_txt == None:
            names = self.names                      
        #names can be provided already as a list too
        elif isinstance(names_txt, list):
            names=names_txt
        #read names from txt file provided
        else:
            with open(names_txt, 'r') as n:
                names = n.read().splitlines()
        
        #remove all lines that contain the 'blank' expression
        if remove_blank: 
            names = [name for name in names if not 'blank' in name]

        #specifies the column to use for the graph depending on whether I want a graph per OD values or not
        if per_OD:
            column_to_plot='average_value_per_OD'
            std_to_plot='std_value_per_OD'
        else:
            column_to_plot='average'
            std_to_plot='std'
        
        #list of method taken from init function
        methods=self.methods
        
        #calculates plot data using the previously defined function 
        plot_data = self.calculate_plot_data(names, methods)
        
        #exports data
        if plot_data_exp:
            plot_data.to_csv(plot_data_exp)

        
        #specifies the bar width to fit the graph depending on the number of methods (manifesting as more bars for one sample)
        bar_x=np.arange(len(names))
        width=1/(len(methods)+1)
        
        #converts Seaborn palettes to ones useable for matplotlib and sets them
        if isinstance(palette,str):
            my_cmap = ListedColormap(sns.color_palette(palette).as_hex())
        else:
            my_cmap = ListedColormap(palette)
        
        #initiate a figure
        fig = plt.figure()
        ax = fig.subplots()
        
        
        #plot the bars of the graph, positioning them to look nice even if more bars for one sample
        i=0
        for method in methods:
            rows = plot_data[plot_data['method'] == method]
            ax.bar(bar_x - width*(len(methods)-1)/2+i*width, 
                   rows[column_to_plot].values,
                   width,
                   label=method,
                   color=my_cmap.colors[i])
                   
            #Here, error bars (standard deviation) are plotted. The size values have been chosen to look nice, 
            #having bars with caps and centered in their respective bars, no matter how many bars 
            #(one for each 'method') per sample are plotted
    
            bar_color = '#666666'
            (_, caps, _) = plt.errorbar(
                bar_x - width*(len(methods)-1)/2+i*width, 
                rows[column_to_plot].values, 
                yerr=rows[std_to_plot].values, 
                fmt='o', 
                markersize=0, 
                capsize=3.7,
                color=bar_color)
            for cap in caps:
                cap.set_markeredgewidth(1)        
            i+=1
        
        #setting graph visuals                                             
        plt.grid(False, axis='x')
        ax.set_axisbelow(True)


        
        #draw legend if requested (default). Only draw if more than one method is used
        if draw_legend==True:
            if len(methods) > 1: 
                ax.legend()
        
        elif draw_legend==False:
            pass
            
        else:
            if len(methods) > 1: 
                ax.legend(bbox_to_anchor=draw_legend)

        #set x_ticks, rotation good for longer names (all I am using)
        ax.set_xticks(bar_x)
        ax.set_xticklabels(names)
        plt.xticks(rotation=60, ha='right')             
        
        #set ylabels (custom defined or automatically from the given data)
        if ylabel:
            ax.set_ylabel(ylabel)
        
        elif self.concentration_units and per_OD: 
            ax.set_ylabel('concentration in ' + self.concentration_units + ' per OD600')    
        elif self.concentration_units and per_OD == False:
            ax.set_ylabel('concentration in ' + self.concentration_units)
        
        elif not self.concentration_units and per_OD:
            ax.set_ylabel('raw MS measurement per OD600')
        else: 
            ax.set_ylabel('raw MS measurement')

        #set title
        if title:
            ax.set_title(title)
        
        #define figure dumensions if specified
        if fig_height:
            fig.set_figheight(fig_height)

        if fig_width:
            fig.set_figwidth(fig_width)
        
        #change maximum of y axis if requested different from default
        if ylim_max:
            ax.set_ylim(top = ylim_max)
        
        #saves export data for when the graph is finished (so even significance asterisks specified separately appear there)
        if output_name:
            self.export.append({'fig':fig, 'output_name': output_name, 'ax':ax})
        
        return fig, ax
            
    def make_barplot_table(self, tableData, 
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
                           draw_legend=True):
        '''Function that builds on top of the make_barplot function. It allows to use a table instead of sample names (can be used for describing each sample by genes modified, etc.). It generates a barplot from the calcualted plot data and uses most the same parameters as make_barplot function.
        
        Parameters:
        tableData - necessary parameter - a csv file that specifies that should be in the x axis description table. First row is the list of sample names. Only samples appearing in the table will be displayed. 
        output_name - name to saving the barplot, typically with .png format
        title - specifies the graph title
        per_OD - is True if I want a graph with concentrations normalised per measured optical density
        remove_blank - will ignore all samples that have 'blank' in the name
        ylabel - change the y asix label
        fig_height - changes saved figure height
        fig_width - changes saved figure width
        palette - allows choosing from pre-defined Seaborn palettes by their Seaborn names
        plot_data_exp -  exports the plot data table for thegraph as csv
        ylim_max - changes the maximum amount shown on y axis. Especially useful if visualising significance asterisks later as they are usually too close to the edge of the graph by default
        draw_legend - by default True, if False, no legend will be drawn
        '''

        #read table data csv
        tableData = pd.read_csv(tableData, header=0, index_col=0)
        
        #helps to check everything is OK, names matching, etc.
        print(tableData)                
        
        #take names from table columns
        names=list(tableData.columns)             
        
        #use make_barplot function with the given parameters
        fig, ax = self.make_barplot(names_txt=names, 
                                    output_name=None, 
                                    title=title, 
                                    per_OD=per_OD, 
                                    remove_blank=remove_blank, 
                                    ylabel=ylabel, 
                                    fig_height=fig_height, 
                                    fig_width=fig_width, 
                                    palette=palette, 
                                    plot_data_exp=plot_data_exp,
                                    ylim_max=ylim_max,
                                    draw_legend=draw_legend)     
        
        #display the table at the bottom, format
        table = ax.table(cellText=tableData.to_numpy(),  
                  colLabels=tableData.columns,        
                  rowLabels=tableData.index,        
                  loc='bottom')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        
        #set limits on x axis so that the table is centered under the respective samples
        ax.set_xlim([-0.5, len(tableData.columns)-0.5])
        
        #remove ticks
        ax.tick_params(axis='x',          # changes apply to the x-axis
                       which='both',      # both major and minor ticks are affected
                       bottom=False,      # ticks along the bottom edge are off
                       top=False,         # ticks along the top edge are off
                       labelbottom=False) # labels along the bottom edge are off

        #save output names if given to be exported when finished
        if output_name:
            self.export.append({'fig':fig, 'output_name': output_name, 'ax':ax})

    
        return fig, ax

       
    def export_dataframe(self, filename):    
        '''Export the data frame used for the figures'''
        self.data.to_csv(filename)
        
            
        
    def make_barplot_sns(self, output_name, names_txt=None):
        '''A method that makes simpler similar graphs using Seaborn. In some cases, it is smoother 
        and looks nicer but offers less flexibility.
        
        Parameters:
        output_name - specify the output file name, usually in .png
        names_txt - a lost of text file with names, analogous to make_barplot'''
        
        
        #set Seaborn style, palette, context (currently not flexible as this function was not used as much)
        sns.set_style('whitegrid')
        sns.set_palette('muted')
        sns.set_context('paper')
    
        #specify the sample names to plot
        if names_txt == None:
            names = self.names
        #names can be also given as a list
        elif isinstance(names_txt, list):
            names=names_txt
            self.data=self.data[self.data['name'].isin(names)]
        #read names from txt file    
        else:
            with open(names_txt, 'r') as n:
                names = n.read().splitlines()
            
            self.data=self.data[self.data['name'].isin(names)]
        
        
        column_to_plot='concentration'        
        
        fig_sns, ax_sns = plt.subplots()
        
        #barplot using Seaborn function
        sns.barplot(x = 'name', 
                          y = column_to_plot, 
                          data=self.data, 
                          hue='method', 
                          capsize=0.1, 
                          order=names,
                          ci='sd', 
                          errwidth=0.9,
                          ax=ax_sns)  
        
        #rotation of xticks
        plt.xticks(rotation=60, ha='right')
  
        #save requested output details
        if output_name:
            self.export.append({'fig':fig_sns, 'output_name': output_name, 'ax':ax_sns})


    def ttest_by_method_paired(self, file_paired=None, methods=None):
        """Method still in development. It gives paired t-test results as a csv table file where for each sample, two methods are compared. Should work seamlessly for two methods and now also for more methods provided, if the methods are specified as a list of indexes in the self.methods. Otherwise, it does just the first two methods. Note that for paired t-test, both methods to be compared must have the same number of measurements.
        
        Parameters:
        file_paired - file name (in csv) for saving the results
        methods - if None, first two methods are compared. If a list of indexes is specified, those are compared"""
        
        #initiate a data frame for output
        self.stats_data_by_method = pd.DataFrame(columns=['name','method1','method2','pvalue'])
        
        #for specific methods
        if methods:
            #subsetting two groups of samples to compare
            for name in self.names:
                sample1_data = self.data[(self.data["name"] == name) & (self.data["method"] == self.methods[methods[0]])]
                sample2_data = self.data[(self.data["name"] == name) & (self.data["method"] == self.methods[methods[1]])]

                #use scipy ttest_rel on the two subsets              
                stat, pvalue = scipy.stats.ttest_rel(
                    sample1_data['concentration'],
                    sample2_data['concentration'])
                
                #save data for the corresponding row of the data frame
                row_ttest = {'name':name, 'method1':self.methods[methods[0]], 'method2':self.methods[methods[1]]}
                row_ttest['pvalue'] = pvalue
                
                #append the row to the resulting data frame
                self.stats_data_by_method = self.stats_data_by_method.append(row_ttest, ignore_index=True)

        #default, for first two methods
        else: 
            #subsetting two groups of samples to compare
            for name in self.names:
                sample1_data = self.data[(self.data["name"] == name) & (self.data["method"] == self.methods[0])]
                sample2_data = self.data[(self.data["name"] == name) & (self.data["method"] == self.methods[1])]
                
                #save data for the corresponding row of the data frame
                stat, pvalue = scipy.stats.ttest_rel(
                    sample1_data['concentration'],
                    sample2_data['concentration'])
                  
                #save data for the corresponding row of the data frame
                row_ttest = {'name':name, 'method1':self.methods[0], 'method2':self.methods[1]}
                row_ttest['pvalue'] = pvalue
                
                #append the row to the resulting data frame
                self.stats_data_by_method = self.stats_data_by_method.append(row_ttest, ignore_index=True)

        #method defined later, gives a column that converts p-value to a widely recognised visualisation by number of stars
        self.fill_dataframe_stars(self.stats_data_by_method)                
        
        #print for easier access
        print(self.stats_data_by_method)
        
        #if filename provided, save to csv
        if file_paired:
            self.stats_data_by_method.to_csv(file_paired)       
        
   
    
    def ttest_independent(self, method = 'all', sample_names='all_names', file_ind=None, group_by=False):
        '''Method still in development. It will take a list of sample names and compare all of them against each other. This is slightly inefficient because each calculation is done twice (hence in development) but still very quick and enough for the purposes used. 
        
        method - specifies which methods should be compared (if only some of interest) can be a string of a specific method or the word 'all'
        sample_names - specify just some samples to compare or all (default)
        file_ind - name of the csv file to save the results
        group-by takes the column which inducates which samples are in fact the same (eg. just different clones) and so should be grouped for the purposes of statistics, not compared against each other or other samples separately. Groups need to be specified as a column of the input file
       ''' 
        
        name_column = 'name'
        
        if sample_names == 'all_names':
            sample_names = self.names
            
        #use groups instead of individual sample names if specified.
        if group_by == True:
            self.groups = self.data.group.unique()    
            sample_names = self.groups
            name_column = 'group'
            
        #between two names, method not relevant (or just one method present)
        if method == 'NaN':
            self.stats_data_independent = pd.DataFrame(columns=['name1','name2','pvalue'])
            
            #subset the samples to compare
            for name1 in sample_names:
                for name2 in sample_names:
                    sample1_data = self.data[(self.data[name_column] == name1)]
                    sample2_data = self.data[(self.data[name_column] == name2)]
                    
                    #if samples have equal lengths, use normal t-test
                    if len(sample1_data) == len(sample2_data):
                        stat, pvalue = scipy.stats.ttest_ind(
                            sample1_data['concentration'],
                            sample2_data['concentration'])
                    
                    #if the samples have not equal lengths, use the Welch t-test
                    else:
                        stat, pvalue = scipy.stats.ttest_ind(
                            sample1_data['concentration'],
                            sample2_data['concentration'], equal_var=False)
    
                    #create a row for dataframe
                    row_ttest = {'name1':name1, 'name2':name2}
                    row_ttest['pvalue'] = pvalue
                    #append the row
                    self.stats_data_independent = self.stats_data_independent.append(row_ttest, ignore_index=True)
        
        #methods to compare specified by their indexes
        elif method != 'all':  
            #initiate data frame
            self.stats_data_independent = pd.DataFrame(columns=['name1','name2','method','pvalue'])
            #select two groups of samples to compare
            for name1 in sample_names:
                for name2 in sample_names:
                    sample1_data = self.data[(self.data[name_column] == name1) & (self.data["method"] == method)]
                    print(name1, name2, sample1_data)
                    
                    sample2_data = self.data[(self.data[name_column] == name2) & (self.data["method"] == method)]
                    
                    #if samples have equal lengths, use normal t-test
                    if len(sample1_data) == len(sample2_data):
                        stat, pvalue = scipy.stats.ttest_ind(
                            sample1_data['concentration'],
                            sample2_data['concentration'])
                    
                    #if the samples have not equal lengths, use the Welch t-test
                    else:
                        stat, pvalue = scipy.stats.ttest_ind(
                            sample1_data['concentration'],
                            sample2_data['concentration'], equal_var=False)
                    
                    #row for output
                    row_ttest = {'name1':name1, 'name2':name2, 'method':method}
                    row_ttest['pvalue'] = pvalue
                    #append row
                    self.stats_data_independent = self.stats_data_independent.append(row_ttest, ignore_index=True)
        
        #if all names and all methods requested to compare against each other
        elif method == 'all':            
            self.stats_data_independent = pd.DataFrame(columns=['name1','name2','method1', 'method2','pvalue'])
            
            #subset the samples
            for name1 in sample_names:
                for name2 in sample_names:
                    for method1 in self.methods:
                        for method2 in self.methods:
                            sample1_data = self.data[(self.data[name_column] == name1) & (self.data["method"] == method1)]
                            sample2_data = self.data[(self.data[name_column] == name2) & (self.data["method"] == method2)]
                            
                            #if samples have equal lengths, use normal t-test
                            if len(sample1_data) == len(sample2_data):
                                stat, pvalue = scipy.stats.ttest_ind(
                                    sample1_data['concentration'],
                                    sample2_data['concentration'])
                            
                            #if the samples have not equal lengths, use the Welch t-test
                            else:
                                stat, pvalue = scipy.stats.ttest_ind(
                                    sample1_data['concentration'],
                                    sample2_data['concentration'], equal_var=False)
            
                            #row for the output
                            row_ttest = {'name1':name1, 'name2':name2, 'method1':method1, 'method2':method2}
                            row_ttest['pvalue'] = pvalue
                            #append the row
                            self.stats_data_independent = self.stats_data_independent.append(row_ttest, ignore_index=True)

        #fill out a column defining the stars visualisation
        self.fill_dataframe_stars(self.stats_data_independent)
        
        #print for easier access
        print(self.stats_data_independent)
        
        #save file if requested
        if file_ind:
            self.stats_data_independent.to_csv(file_ind)
        

    @staticmethod    
    def p_value_to_star(pvalue):
        '''Calculates the number of stars to display based on the p-value visualisation conventions'''
        if pvalue <= 0.0001:
            return "****"
        elif pvalue <= 0.001:
            return "***"
        elif pvalue <= 0.01:
            return "**"
        elif pvalue <= 0.05:
            return "*"
        else:
            return "ns"      
        
    def fill_dataframe_stars(self, file):
        '''Fills out a column in the dataframe indicating the number of stars calculated from p-value (saved as pvalue column) using the p_value_to_star function'''
        
        file['star'] = \
            file['pvalue'].apply(lambda x: MSData.p_value_to_star(x))
        
        print(file)

    def annot_stat(self, star, x1, x2, y, h, col='k'):
        '''Plots a graphic representation of the significance (usually stars)
        
        Parameters:
        star - text to be written, usually different amount of asterisks
        x1 - lower x position of the 'leg'
        x2 - higher x position of the 'leg'
        y - y position of the bar
        h - height of the bar above the 'legs'
        '''
        
        ax = self.export[-1]['ax']
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.5, c=col)
        ax.text((x1+x2)*.5, y+h, star, ha='center', va='bottom', color=col)
        

        
        
      
        

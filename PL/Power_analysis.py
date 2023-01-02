# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 12:35:26 2022

The script modifies the all files in a folder to match the hight of all data.
We are looking for bumps in intensity differences in the data.
@author: Alex
"""

from pandas import read_csv
import pandas as pd
import numpy as np
import os.path
from os import listdir
from scipy.optimize import curve_fit

def import_csv(path):
    """
    
    Returns:
    -------
    None.

    """
    data = list()
    file = read_csv(path,header = None)
    for i in range(len(file.columns)):
        data.append(file[i].tolist())
    del file
            
    return data

def create_csv(path):
    with open(path, 'w') as file: 
        pass 
    file.close()

def change_type(x):
    y = []
    for i in x:
        y.append(float(i))
    return y

def add_column2(path,data, column_name = ''):
    # Add column to csv file
    try:
        file = read_csv(path,header=None)
    except:
        pass

    try:
        column_len = len(file.columns)
    except:
        column_len = 0
    

    temp_data = [column_name] + data
    del data
    
    try:
        file[column_len+1] = temp_data
    except:
        file = pd.DataFrame(temp_data)
        
    file.to_csv(path,index=False,header=None)


def find_factor_function(data,a):
    # data1 > data2
    return data*a

def find_factor(data1,data2):
    # data1 < data2
    popt, pcov = curve_fit(find_factor_function,data1,data2, maxfev=100000)
    return popt

def __main__(IMPORT_PATH, EXPORT_PATH="D:\\PL_results_default"):
    """
    Creates new data columns in each csv file.
    Creates Energy column (hc/lambda) from column 0
    Creates Mean Intensity column from n next columns
    
    """
    import_path = IMPORT_PATH
    export_path = EXPORT_PATH
    isExist = os.path.exists(export_path)
    
    if not isExist:
        os.makedirs(export_path)
    
    
    filenames = listdir(import_path)
    folder_list = [ filename for filename in filenames]
    
    export_path_csv = export_path + "\\" + folder_list[0]
    create_csv(export_path_csv)
    
    ALL_DATA = [[] for x in range(len(folder_list))]
    i = 0
    for file in folder_list: # what day data was taken
        file_path = import_path + "\\" + file
        data = import_csv(file_path)[6]
        del data[0]
        ALL_DATA[i] = change_type(data)
        i += 1
    
    data = import_csv(file_path)[5] # Uses the latest used path
    del data[0]
    add_column2(export_path_csv,data, 'eV')
    del data
    ### AT THIS POINT I HAVE ALL INTENSITIES AND FILES NAMES {ALL_DATA and folder_list}
    for i in range(len(folder_list)):
        #a = find_factor(ALL_DATA[i],ALL_DATA[-1])
        a = [1.0]
        b = [float(a[0])*x for x in ALL_DATA[i]]
        final_data = list()
        for item1, item2 in zip(ALL_DATA[-1], b):
            item = item1 - item2
            final_data.append(item)
        
        add_column2(export_path_csv,final_data, folder_list[i])

            
    return 0 #2D array




Mphys_path = 'D:\\MPhys\\Analyse\\C_1nm_2s_Wdiff'
__main__(Mphys_path)



# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 12:40:37 2022

The program removes incontinuity due to SynerJY software spectra connection.

When taking the spectra, software takes N number of acquisitions and then
puts the data together. X value (wavelength) can be repeated.
In general, discontinuity in internsity (Y value) can be seen as a huge difference
between 2 adjoined X values. 

@author: Alex
"""

'''
from pandas import read_csv
import matplotlib.pyplot as plt
import pandas as pd

def import_csv(path):
    data = list()
    file = read_csv(path,header=None)
    for i in range(len(file.columns)):
        data.append(file[i].tolist())
    del file

    for i in data:
        i.pop(0)
    
    return data

def create_csv(path):
    with open(path, 'w') as file: 
        pass 
    file.close()

def add_column(path,data):
    
    file = read_csv(path,header=None)
    file[len(file.columns)+1] = data
    file.to_csv(path,index=False,header=None)

def add_column2(path,data, column_name = ''):

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

def filter_condition(x):
    positions = []
    for i in range(len(x)):
        if float(x[i])>0.11:
            positions.append(i)
    return positions
'''
def adjoined_difference(x):
    diff = []
    for i in range(len(x)-1):
        diff.append((float(x[i+1])-float(x[i])))
    return diff


def change_type(x):
    y = []
    for i in x:
        y.append(float(i))
    return y

def remove_discontinuity(intensity,x=1):
    """
    Parameters
    ----------
    x : int
        Indicates the range of spectra.
    1: 330nm-630nm

    Returns
        Intensity
    """
    # Python does not have easy way to implements switch{}
    intensity = change_type(intensity)
    intensity_diff = adjoined_difference(intensity)
    #330_630nm
    if x==1:
        inten_d =[]
        # Positions start at 2033 entry [2032 position in the list], the next one is =+1014 till 8117
        for j in range(7):
            t = 1019 + j*1014 - 1
            inten_d.append(float(intensity_diff[t])+1.0)
            inten =sum(inten_d)
            for i in range(1014):
                intensity[t+i+1] -= inten
        t += 1014
        k = len(intensity) - t
        inten_d.append(float(intensity_diff[t])+1.0)
        inten =sum(inten_d)
        for i in range(k-1):
            intensity[t+i+1] -= inten

    elif x==2:
        print('Put the code different range')

    else:
        print('Not defined, initial values returned')
    return intensity

"""
def __main__():
    import_path = 'C:\\Users\\Alex\\Documents\\GitHub\\MPhysProject\\black_body_330_630.csv'
    export_path = 'C:\\Users\\Alex\\Documents\\GitHub\\MPhysProject\\continous_black_body_330_630.csv'

    create_csv(export_path)

    data = import_csv(import_path)

    x = data[0]
    y = data[2]
    del data
    z = remove_discontinuity(y)

    add_column2(export_path, x)
    add_column2(export_path, y)
    add_column2(export_path, z)
    
"""
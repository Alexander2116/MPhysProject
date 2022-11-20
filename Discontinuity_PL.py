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


from pandas import read_csv
import matplotlib.pyplot as plt
import pandas as pd

def import_csv(path):
    """
    
    Returns:
    -------
    None.

    """
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

def adjoined_difference(x):
    diff = []
    for i in range(len(x)-1):
        diff.append((float(x[i+1])-float(x[i]))/float(x[i]))
    return diff

def filter_condition(x):
    positions = []
    for i in range(len(x)):
        if float(x[i])>0.11:
            positions.append(i)
    return positions

def change_type(x):
    y = []
    for i in x:
        y.append(float(i))
    return y

def adjust(intensity):
    intensity = change_type(intensity)
    intensity_diff = adjoined_difference(intensity)
    print(intensity_diff)
    points = filter_condition(intensity_diff)
    print(points)
    # Move intensity
    for i in range(len(points)-1):
        for j in range(points[i], points[i+1]-1):
            intensity[j+1] -= intensity_diff[j]
    return intensity

path = 'C:\\Users\\Alex\\Documents\\GitHub\\MPhysProject\\R7_1nm_1s_0.257mW_295.16K.csv'
path2 = 'C:\\Users\\Alex\\Documents\\GitHub\\MPhysProject\\test.csv'

create_csv(path2)

data = import_csv(path)

x = data[0]
y = data[3]
del data
z = adjust(y)

#add_column2(path2, x)
#add_column2(path2, y)
#add_column2(path2, z)

#plt.figure(figsize=(40,21))
#plt.scatter(x, y, marker='.')
#plt.plot(x, y, ',')
#plt.xticks([])
#plt.yticks([])

#plt.xlabel('xlabel')
#plt.ylabel('ylabel')
#plt.show()

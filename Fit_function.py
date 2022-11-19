# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 12:54:11 2022

Fits function to bulb spectra.
It will allow to find a fuction describing bulb spectra.
The data is taken from range 330nm and 630nm with step ~0.04nm

@author: Alex
"""

import matplotlib.pyplot as plt
from pandas import read_csv

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

path = 'C:\\Users\\Alex\\Documents\\GitHub\\MPhysProject\\black_body_330_630.csv'
data = import_csv(path)

x = data[0]
y = data[1]
del data

plt.scatter(x, y, label= "stars", color= "green", marker= "*", s=30)
plt.axis([min(x), max(x), min(y), max(y)])

plt.xlabel('xlabel')
plt.ylabel('ylabel')
plt.show()


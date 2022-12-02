# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 00:11:22 2022

Program to fit function to traditional DLTS spectra (different rate windows)

@author: Alex
"""

import numpy as np
import scipy.signal
from pandas import read_csv
import matplotlib.pyplot as plt

def import_csv(path, remove_first_list = False):
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
    
    # Remove first item in each column (column name)
    if remove_first_list == True:
        for i in data:
            i.pop(0)
            
    return data

def life_time(T,P1,P2):
    """
     P1 = A*B*sigma*exp(S/k) , where A and B are:
     N = A T^3/2
     v = B T^1/2
     A, B can be taken from literautre
     P2 = H (or delta E)
    """
    k = 8.617333262*10**(-5) # eV/K
    return P1* T**2 * np.exp(P2/(k*T))

def end_of_peak(data,cond = 5*10**(-4)):
    x,y = data
    m = np.max(y)
    m_idx = y.index(m)
    
    len_y = len(y)
    end_pos = 0
    start_pos = 0
    ## go to right
    for i in range(m_idx,len_y):
        end_pos = i
        if y[end_pos]<cond:
            break
    ## go to left
    for i in range(0,m_idx):
        start_pos = m_idx - i
        if y[start_pos]<cond:
            break
        
    return x[start_pos:end_pos], y[start_pos:end_pos]

def separate_peaks(data):
    # Separate data to N lists, where N is the number of visible (big) peaks
    x,y = data # Must be 2D data
    peaks,_ = scipy.signal.find_peaks(y,height=0.001, threshold = 0.0002)
    min_b_peaks = []
    min_b_peaks_idx = [0]
    data_ret = []
    
    if len(peaks)>1:
        for i in range(len(peaks)-1):
            min_b_peaks.append(np.min(y[peaks[i]:peaks[i+1]]))
            
        for i in min_b_peaks:
            min_b_peaks_idx.append(y.index(float(i)))
        
        min_b_peaks_idx.append(len(y))
        del min_b_peaks
    else:
        del min_b_peaks
    
    if len(min_b_peaks_idx)>0:
        print(min_b_peaks_idx)
        for i in range(len(min_b_peaks_idx)-1):
            da = [x[min_b_peaks_idx[i]:min_b_peaks_idx[i+1]],y[min_b_peaks_idx[i]:min_b_peaks_idx[i+1]]]
            data_ret.append(end_of_peak(da))
            
    else:
        data_ret = [end_of_peak(data)]

    return data_ret


PATH = 'D:\\MPhys_DLTS\\Irr370-sC\\test.csv'
data = import_csv(PATH)
data = separate_peaks(data)

for da in data:
    x,y = da
    plt.plot(x,y,',')
    plt.show()
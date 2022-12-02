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
from scipy.optimize import curve_fit


### GLOBAL ####
RATE_WINDOW_MULTIPLIER= 1527
## Global dictionary, key is the emission rate
## I put only t1 because relation between t1 and t2 is: t2=2.5*t1
T1_VALUES = {
    4: 1.525875*10**(-1),
    10: 6.1035*10**(-2),
    20: 3.05175*10**(-2),
    50: 1.2208*10**(-2),
    80: 7.629375*10**(-3),
    200: 3.05175*10**(-3),
    400: 1.525875*10**(-3),
    1000: 6.1035*10**(-4)
    }


### DEFINED FUNCTION ####
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
    This is actually emission rate = 1/tau
     P1 = A*B*sigma*exp(S/k) , where A and B are:
     N = A T^3/2
     v = B T^1/2
     A, B can be taken from literautre
     P2 = H (or delta E)
    """
    k = 8.617333262*10**(-5) # eV/K
    return P1* T**2 * np.exp(P2/(k*T))

def capacity_dif(T, C_m,P1,P2, rate_window=80):
    t1= T1_VALUES.get(int(rate_window))
    t2= 2.5*t1
    tau = life_time(T,P1,P2) # !!! This is in fact 1/tau !!!
    return C_m*np.exp(-tau)*(np.exp(t1)-np.exp(t2))

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

def fit_fun(data,rate_window =20):
    x,y = data
    popt, pcov = scipy.optimize.curve_fit(capacity_dif,[x,y],y)
    return popt

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

# Object that stores all essential informations and allows to 
class CCF:
    # CAPACITANE CURVE FINDER
    RATE_WINDOW = 0
    TEMP = [] # Temperature - x data
    CAP = [] # Capacity - y data
    
    def __init__(self,x,y,rate):
        self.TEMP = x
        self.CAP = y
        self.RATE_WINDOW = rate
        print('ready')




PATH = 'D:\\MPhys_DLTS\\Irr370-sC\\test.csv'
data = import_csv(PATH)
data = separate_peaks(data)

for da in data:
    x,y = da
    print(fit_fun(da))
    plt.plot(x,y,',')
    plt.show()
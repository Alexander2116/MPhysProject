# -*- coding: utf-8 -*-
"""
Created on Fri Dec  2 00:11:22 2022

Program to fit function to traditional DLTS spectra (different rate windows)
VERSION 2. Force to fit as many as possible
@author: Alex
"""

import numpy as np
import scipy.signal
from pandas import read_csv
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.fft import fft, fftfreq, ifft
import DLTS_DataCut_json as DLTSJS
from os import listdir
import warnings

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


def change_json_values(data):
    return [float(x) for x in data]


# Object that stores all essential informations and allows to 
class CCF:
    # CAPACITANE CURVE FINDER
    RATE_WINDOW = 0
    TEMP = [] # Temperature - x data
    CAP = [] # Capacity - y data
    NO_PEAKS = 3
    
    P1_LIST = []
    P2_LIST = []
    C_m_LIST = []
    
    RATE_WINDOW_MULTIPLIER= 1527
    popt = []
    
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
    
    def __init__(self,x,y,rate):
        self.TEMP = x
        self.CAP = y
        self.RATE_WINDOW = rate
        #print('ready')
    
    def number_of_peaks(self,n):
        self.NO_PEAKS = n

    def find_max_index(self,x):
        m = np.max(x)
        m_idx = x.index(m)
        return m_idx


    def life_time(self,T,P1,P2):
        k = 8.617333262*10**(-5) # eV/K
        #return P1 * ((T-self.T0)**2) * np.exp(-P2/(k*(T+self.T0)))
        return P1 * T**2 * np.exp(-P2/(k*T))


    def capacity_dif(self,T,P1,P2,C_m):
        rate_window = self.RATE_WINDOW
        t1= self.T1_VALUES.get(int(rate_window))
        t2= 2.5*t1
        tau = self.life_time(T,P1,P2) # !!! This is in fact 1/tau !!!
        return C_m * (np.exp(-t1*tau)-np.exp(-t2*tau))
    
    def fit_all(self,T,*arg):
        result = []
        for i in range(int(len(arg)/3)):
            P1 = arg[0 + 3*i]
            P2 = arg[1 + 3*i]
            C_m = arg[2 + 3*i]
            value = self.capacity_dif(T,P1,P2,C_m)
            result.append(value)
            
        return sum(result)

    def find_param(self):
        #self.norm_temp()
        x = self.TEMP
        y = self.CAP
        n = self.NO_PEAKS
        p = [1] * (n*3)
        bound_min = [0] * (n*3)
        bound_max = [0] * (n*3)
        inc = 0.08/n
        for i in range(n):
            p[0 + 3*i]= 1278808 # S
            p[1 + 3*i]= 0.12+inc*i # E
            p[2 + 3*i]= 0.1 # C_m
            bound_max[0 + 3*i] = np.inf
            bound_max[1 + 3*i] = 4
            bound_max[2 + 3*i] = np.inf
        # P1, P2, Cm
        #self.popt, pcov = curve_fit(self.fit_all, x, y, p0=params_0, maxfev=5000,bounds=([0,0,0],[np.inf,4,np.inf]))
        self.popt, pcov = curve_fit(self.fit_all,x,y, p0=p, maxfev=100000, bounds=(bound_min,bound_max))
        return self.popt


    def plot_fit(self):
        x = self.TEMP
        y = self.CAP
        xdata = np.linspace(np.min(x), np.max(x), 500)
        ydata = [0]*500
        p = self.popt
        n = self.NO_PEAKS
        
        plt.plot(x,y,'o')
        for i in range(n):
            plt.plot(xdata,self.capacity_dif(xdata,p[0+3*i],p[1+3*i],p[2+3*i]),label="E="+ str(round(p[1+3*i],3)))
            ydata += self.capacity_dif(xdata,p[0+3*i],p[1+3*i],p[2+3*i])
        plt.plot(xdata,ydata,label="Sum of all peaks")
        plt.legend()
        plt.title('Rate Window = '+str(self.RATE_WINDOW))
        plt.show()
        
    


def __main__(load_data_path):
    filenames = listdir(load_data_path)
    for fp in filenames:
        import_path = load_data_path + '\\' + fp
        JS = DLTSJS.deal_json(import_path)
        x1 = change_json_values(JS.read()['data1']) # Temp
        y1 = change_json_values(JS.read()['data2']) # dC

        win_rate = int(JS.read()['rate window'])
        del JS
        
        x1 = x1[10:47]
        y1 = y1[10:47]
        
        FCC = CCF(x1,y1,win_rate)
        FCC.number_of_peaks(3)
        FCC.find_param()
        FCC.plot_fit()
        


warnings.filterwarnings('ignore')
PATH = 'D:\\MPhys_DLTS\\JSON_test'
__main__(PATH)

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

    return x[start_pos:end_pos], y[start_pos:end_pos], start_pos


def separate_peaks(data):
    # Separate data to N lists, where N is the number of visible (big) peaks
    x,y = data # Must be 2D data
    peaks,_ = scipy.signal.find_peaks(y,distance=5,height = 0.002) #,height=0.001, threshold = 0.0002
    final_peaks = []
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
        for i in range(len(min_b_peaks_idx)-1):
            da = [x[min_b_peaks_idx[i]:min_b_peaks_idx[i+1]],y[min_b_peaks_idx[i]:min_b_peaks_idx[i+1]]]
            final_peaks.append(peaks[i] - min_b_peaks_idx[i]- end_of_peak(da)[2]-2)
            data_ret.append([end_of_peak(da)[0],end_of_peak(da)[1]])
            
    else:
        data_ret = [end_of_peak(data)]
        final_peaks.append(peaks[0])

    return data_ret, final_peaks

def change_json_values(data):
    return [float(x) for x in data]

def separate(data, sep_point):
    x,y =[],[]
    x1,y1 =[],[]
    for i in range(len(data[0])):
        if float(data[0][i]) <= float(sep_point):
            x.append(data[0][i])
            x1.append(data[1][i])
        else:
            y.append(data[0][i])
            y1.append(data[1][i])
            
    return [x,x1],[y,y1]


# Object that stores all essential informations and allows to 
class CCF:
    # CAPACITANE CURVE FINDER
    RATE_WINDOW = 0
    TEMP = [] # Temperature - x data
    CAP = [] # Capacity - y data
    T0 = 0
    PEAK_INDEX = 0
    
    T0_LIST = []
    P1_LIST = []
    P2_LIST = []
    C_m_LIST = []
    
    C_m = 0
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
    
    def __init__(self,x,y,rate,peak_idx = 0):
        self.TEMP = x
        self.CAP = y
        self.RATE_WINDOW = rate
        m = self.find_max_index(y)
        self.T0 = x[m]
        self.C_m = y[m]
        self.PEAK_INDEX = peak_idx
        #print('ready')
    
    def insert_lists(self,P1,P2,T0,C_m):
        self.T0_LIST = T0
        self.P1_LIST = P1
        self.P2_LIST = P2
        self.C_m_LIST = C_m
        
    def find_max_index(self,x):
        m = np.max(x)
        m_idx = x.index(m)
        return m_idx
        
    def norm_temp(self):
        t = self.TEMP
        minT = np.min(t)
        self.TEMP = [x-minT for x in t]
        
    # COPY FROM ABOVE
    def life_time(self,T,P1,P2):
        k = 8.617333262*10**(-5) # eV/K
        #return P1 * ((T-self.T0)**2) * np.exp(-P2/(k*(T+self.T0)))
        return P1 * T**2 * np.exp(-P2/(k*T))
    
    def set_T0(self,value):
        self.T0 = value
        
    def set_Cm(self,value):
        self.C_m = value
        
    # COPY FROM ABOVE
    def capacity_dif(self,T,P1,P2,C_m):
        rate_window = self.RATE_WINDOW
        t1= self.T1_VALUES.get(int(rate_window))
        t2= 2.5*t1
        tau = self.life_time(T,P1,P2) # !!! This is in fact 1/tau !!!
        #return np.exp(-tau) *self.C_m #* np.abs(np.exp(t1)-np.exp(t2))
        return C_m * (np.exp(-t1*tau)-np.exp(-t2*tau))
    
    def multiple_peaks(self,T):
        T0 = self.T0_LIST
        P1 = self.P1_LIST 
        P2 =self.P2_LIST
        C_m= self.C_m_LIST
        value = 0
        for i in range(len(T0)):
            self.set_T0(T0[i])
            tau = self.life_time(T,P1[i],P2[i])
            value += np.exp(-tau) *C_m[i]
            
        return value

    def find_param(self):
        #self.norm_temp()
        x = self.TEMP
        y = self.CAP
        # P1, P2, Cm
        guesses = [1278808,0.3,0.1] 
        
        # Set weights to the points
        sigma = np.ones(len(x))*0.000001
        
        
        ypeak = self.PEAK_INDEX
        sigma[ypeak] = 0.0000001
        sigma[[ypeak-1,ypeak+1]] = 0.0000002
        try:
            sigma[[ypeak-2,ypeak+2]] = 0.0000004
        except:
            print()
        
        self.popt, pcov = curve_fit(self.capacity_dif, x, y,guesses,maxfev=5000,bounds=([0,0,0],[np.inf,4,np.inf]),sigma=sigma)
        return self.popt
    
    def get_values(self):
        E = self.popt[1]
        S = self.popt[0]
        return S,E,self.T0, self.popt[2]
    
    
    def plot_multiple(self):
        x = self.TEMP
        y = self.CAP
        xdata = np.linspace(np.min(x), np.max(x), 500)
        plt.plot(xdata,self.multiple_peaks(xdata))
        plt.plot(x,y,',')
        plt.show()
        
    def plot_fit(self):
        x = self.TEMP
        y = self.CAP
        xdata = np.linspace(np.min(x), np.max(x), 500)
        p = self.popt
        E = round(self.get_values()[1],2)
        S = round(self.get_values()[0],4)
        plt.plot(xdata,self.capacity_dif(xdata,p[0],p[1],p[2]))
        plt.plot(x,y,'o')
        plt.text(np.max(x)*1.05, np.max(y),"S = " + str(S), fontsize = 20)
        plt.text(np.max(x)*1.05, np.max(y)*6/9,"E = " + str(E), fontsize = 20)
        plt.text(np.max(x)*1.05, np.max(y)*1/9,"Rate = " + str(self.RATE_WINDOW), fontsize = 20)
        plt.text(np.max(x)*1.05, np.max(y)*3/9,"C_m = " + str(round(p[2],2)), fontsize = 20)
        plt.show()
        
    

def __main__(load_data_path):
    filenames = listdir(load_data_path)
    for fp in filenames:
        import_path = load_data_path + '\\' + fp
        
        JS = DLTSJS.deal_json(import_path)
        x1 = change_json_values(JS.read()['data1']) # Temp
        y1 = change_json_values(JS.read()['data2']) # dC

        data = [x1,y1]
        win_rate = int(JS.read()['rate window'])
        del JS
        
        sep_data = separate_peaks(data)
        sep_data = [x for x in sep_data if x != ([],[])]


        P1, P2, T0, C_m = [],[],[],[]
        
        for i in range(len(sep_data[0])):
            x,y = sep_data[0][i]
            peak_idx = sep_data[1][i]
            
            FCC = CCF(x,y,win_rate,peak_idx)
            FCC.find_param()
            plt.title(fp)
            FCC.plot_fit()
            P1.append(FCC.get_values()[0])
            P2.append(FCC.get_values()[1])
            T0.append(FCC.get_values()[2])
            C_m.append(FCC.get_values()[3])
            del FCC
        
        FCC = CCF(x1,y1,win_rate)
        FCC.insert_lists(P1, P2, T0, C_m)
        FCC.plot_multiple()
        
        
        
warnings.filterwarnings('ignore')
PATH = 'D:\\MPhys_DLTS\\JSON_test'
__main__(PATH)
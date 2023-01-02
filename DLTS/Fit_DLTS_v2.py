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

plt.rc('xtick', labelsize=12)
plt.rc('ytick', labelsize=12)

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


def chi_sq(measured,expected):
    chi_sqr = 0
    for i in range(len(measured)):
        chi_sqr += ((measured[i]-expected[i])**2) /(abs(expected[i]))
    return chi_sqr


# Object that stores all essential informations and allows to 
class CCF:
    # CAPACITANE CURVE FINDER
    RATE_WINDOW = 0
    TEMP = [] # Temperature - x data
    CAP = [] # Capacity - y data
    NO_PEAKS = 3
    
    # Multiply P1 to receive cross section (cm^2)
    ACS_GaN = 1/(6.493*10**20) # coefficient to change P1 to apparent cross section
    
    P1_LIST = []
    P2_LIST = []
    C_m_LIST = []
    
    RATE_WINDOW_MULTIPLIER= 1527
    popt = []
    pcov = []
    
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
    
    def export_popt(self):
        return self.popt
    
    def import_popt(self,popt):
        self.popt = popt
    
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
        bound_min = [0] * (n*3)
        bound_max = [0] * (n*3)
        for i in range(n):
            bound_max[0 + 3*i] = np.inf
            bound_max[1 + 3*i] = 4
            bound_max[2 + 3*i] = np.inf
        
        if len(self.popt) == 0:
            p = [1] * (n*3)
            inc = 0.04/n
            for i in range(n):
                p[0 + 3*i]= 1278808 # S
                p[1 + 3*i]= 0.12+inc*i # E
                p[2 + 3*i]= 0.1 # C_m
        else:
            p = self.popt
        # P1, P2, Cm
        #self.popt, pcov = curve_fit(self.fit_all, x, y, p0=params_0, maxfev=5000,bounds=([0,0,0],[np.inf,4,np.inf]))
        self.popt, self.pcov = curve_fit(self.fit_all,x,y, p0=p, maxfev=100000, bounds=(bound_min,bound_max))
        return self.popt

    

    def cross_sections(self):
        cross_section = []
        p = self.popt
        for i in range(self.NO_PEAKS):
            cross_section.append(p[0+3*i]*self.ACS_GaN)
            
        return cross_section


    def plot_fit(self):
        x = self.TEMP
        y = self.CAP
        xdata = np.linspace(np.min(x), np.max(x), 500)
        ydata = [0]*500
        p = self.popt
        pEerr = np.sqrt(self.pcov[1][1])
        n = self.NO_PEAKS
        
        
        plt.plot(x,y,'o')
        for i in range(n):
            pEerr = np.sqrt(self.pcov[1+3*i])
            pEerr = pEerr[~np.isnan(pEerr)]
            pEerr = np.min(pEerr)
            
            Eerror = ' ('+ str(round(pEerr,4)) +')'
            
            plt.plot(xdata,self.capacity_dif(xdata,p[0+3*i],p[1+3*i],p[2+3*i]),label="$\Delta$E = "+ str(round(p[1+3*i],3))+Eerror+ ' eV')
            ydata += self.capacity_dif(xdata,p[0+3*i],p[1+3*i],p[2+3*i])
        if n>1:
            plt.plot(xdata,ydata,label="Sum of all peaks")
        plt.text(np.min(x),0.004,'Rate Window = '+str(self.RATE_WINDOW) + ' $s^{-1}$',
                 bbox=dict(facecolor='none', edgecolor='grey'))
        plt.text(x[y.index(max(y))]*1.05,max(y)*0.95,'E1',fontsize=14)
        plt.legend()
        #plt.title('Rate Window = '+str(self.RATE_WINDOW))
        plt.xlabel("Temperature (K)",fontsize = 14)
        plt.ylabel('$\Delta$C (pF)' ,fontsize = 14)
        plt.show()
        
        
    def plot_extra(self):
        x = self.TEMP
        y = self.CAP
        xdata = np.linspace(np.min(x), np.max(x), 500)
        p = self.popt
        n = self.NO_PEAKS
        yexpt = [0]*len(y)
        relativ = [0]*len(y)
        peak_data = [[] for x in range(len(y))]
        
        
        for i in range(n):
            for j in range(len(x)):
                yexpt[j] += self.capacity_dif(x[j],p[0+3*i],p[1+3*i],p[2+3*i])
                a = y[j]-self.capacity_dif(x[j],p[0+3*i],p[1+3*i],p[2+3*i])
                peak_data[i].append(a)
        
        for j in range(len(y)):
            relativ[j] = y[j] - yexpt[j]
            
        chi_sqrt = sum([(abs(i)/max(relativ))**2 for i in relativ])/(len(y)-n*3)

        plt.plot(xdata,xdata*0)
        plt.ylim([-0.0012,0.0012])
        plt.plot(x,relativ,'o',label="Chi = " + str(round(chi_sqrt,4)))
        plt.legend()
        plt.show()
        
        plt.plot(xdata,xdata*0)
        plt.ylim([-0.002,0.015])
        for i in range(n):
            plt.plot(x,peak_data[i],'o', label=str(i))
        plt.legend()
        plt.show()


def __main__(load_data_path,N,extras = False,comparison = False):
    filenames = listdir(load_data_path)
    popts = [[] for x in range(len(filenames))]
    iii = 0
    cross_sections = []
    for fp in filenames:
        import_path = load_data_path + '\\' + fp
        JS = DLTSJS.deal_json(import_path)
        x1 = change_json_values(JS.read()['data1']) # Temp
        y1 = change_json_values(JS.read()['data2']) # dC

        win_rate = int(JS.read()['rate window'])
        

        del JS
        
        if win_rate == 80:
            x1 = x1[6:37]
            y1 = y1[6:37]
        elif win_rate == 200:
            x1 = x1[6:38]
            y1 = y1[6:38]
        else:
            x1 = x1[10:47]
            y1 = y1[10:47]
            
        """
        if win_rate == 80:
            x1 = x1[38:]
            y1 = y1[38:]
        elif win_rate == 200:
            x1 = x1[39:]
            y1 = y1[39:]
        else:
            x1 = x1[48:]
            y1 = y1[48:]
        """
        
        FCC = CCF(x1,y1,win_rate)
        FCC.number_of_peaks(N)
        FCC.find_param()
        popts[iii].append(FCC.export_popt())
        FCC.plot_fit()
        if extras == True:
            FCC.plot_extra()
        iii += 1
        cross_sections.append(FCC.cross_sections())
        del FCC
    
    for pp in popts:
        a = list(pp[0])
        print(a[1::3])
        
    for cs in cross_sections:
        print(cs)
    
    if comparison == True:
        plt.plot([0],[0])
        plt.show()
        ### Force each values
        for fp in filenames:
            import_path = load_data_path + '\\' + fp
            JS = DLTSJS.deal_json(import_path)
            x1 = change_json_values(JS.read()['data1']) # Temp
            y1 = change_json_values(JS.read()['data2']) # dC
    
            win_rate = int(JS.read()['rate window'])
            del JS

            if win_rate == 80:
                x1 = x1[6:37]
                y1 = y1[6:37]
            elif win_rate == 200:
                x1 = x1[6:38]
                y1 = y1[6:38]
            else:
                x1 = x1[10:47]
                y1 = y1[10:47]
            

            for pp in popts:
                FCC = CCF(x1,y1,win_rate)
                FCC.import_popt(list(pp[0]))
                FCC.number_of_peaks(N)
                FCC.find_param()
                FCC.plot_fit()
                del FCC
            plt.plot([0],[0])
            plt.show()

def __main2__(load_data_path,N,extras = False,comparison = False):
    filenames = listdir(load_data_path)
    popts = [[] for x in range(len(filenames))]
    iii = 0
    cross_sections = []
    for fp in filenames:
        import_path = load_data_path + '\\' + fp
        JS = DLTSJS.deal_json(import_path)
        x1 = change_json_values(JS.read()['data1']) # Temp
        y1 = change_json_values(JS.read()['data2']) # dC

        win_rate = int(JS.read()['rate window'])
        del JS

        
        FCC = CCF(x1,y1,win_rate)
        FCC.number_of_peaks(N)
        FCC.find_param()
        popts[iii].append(FCC.export_popt())
        FCC.plot_fit()
        if extras == True:
            FCC.plot_extra()
        iii += 1
        cross_sections.append(FCC.cross_sections())
        del FCC
    
    for pp in popts:
        a = list(pp[0])
        print(a[1::3])
    
    for cs in cross_sections:
        print(cs)
    
    if comparison == True:
        plt.plot([0],[0])
        plt.show()
        ### Force each values
        for fp in filenames:
            import_path = load_data_path + '\\' + fp
            JS = DLTSJS.deal_json(import_path)
            x1 = change_json_values(JS.read()['data1']) # Temp
            y1 = change_json_values(JS.read()['data2']) # dC
    
            win_rate = int(JS.read()['rate window'])

            
            for pp in popts:
                FCC = CCF(x1,y1,win_rate)
                FCC.import_popt(list(pp[0]))
                FCC.number_of_peaks(N)
                FCC.find_param()
                FCC.plot_fit()
                del FCC
            plt.plot([0],[0])
            plt.show()

warnings.filterwarnings('ignore')
PATH = 'D:\\MPhys_DLTS\\JSON_E1'
__main__(PATH,4)

#PATH = 'D:\\MPhys_DLTS\\JSON_E3'
#__main2__(PATH,1)


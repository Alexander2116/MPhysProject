# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 12:54:11 2022

Fits function to bulb spectra.
It will allow to find a fuction describing bulb spectra.
The data is taken from range 330nm and 630nm with step ~0.04nm

@author: Alex
"""

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
    
    return data

def change_type(x):
    y = []
    for i in x:
        y.append(float(i))
    return y

class Bulb_spectra():
    """
    The maximal range for the spectra should be 330-630nm
    """
    data = [] # 0: wavelength, 2: intensity
    wave = []
    intensity = []
    is_full_range = False
    def __init__(self):
        ### Path to black body data [0: wavelength, 1: Intensity, 2: Continous intensity]
        path = 'C:\\Users\\Alex\\Documents\\GitHub\\MPhysProject\\continous_black_body_330_630.csv'
        self.data = import_csv(path)
        self.wave = change_type(self.data[0])
        self.intensity = self.data[2]
        del self.data
        
    def Full_range(self):
        self.is_full_range = True
    
    def Bulb_response(self, wavelength):
        # Wavelength = single float value
        lam = min(self.wave, key=lambda x:abs(float(x)-float(wavelength)))
        idx = self.wave.index(float(lam))
        
        return self.intensity[idx]
    
    
    def More_accurate(self,wavelength):
        lam = min(self.wave, key=lambda x:abs(float(x)-float(wavelength)))
        idx = self.wave.index(float(lam))
        
        if self.wave[idx-1] < wavelength < self.wave[idx]:
            a = wavelength - self.wave[idx-1]
            b =  self.wave[idx] - wavelength
            return (self.intensity[idx-1]*b + self.intensity[idx]*a)/(a+b)
        
        elif self.wave[idx] < wavelength < self.wave[idx+1]:
            a = wavelength - self.wave[idx]
            b =  self.wave[idx+1] - wavelength
            return (self.intensity[idx]*b + self.intensity[idx+1]*a)/(a+b)
        
        elif wavelength == self.wave[idx]:
            return self.intensity[idx]
        
        else:
            return self.intensity[idx]
        
    def Spectra(self, wavelength):
        if self.is_full_range == True:
            idx = self.wave.index(float(wavelength))
            return self.intensity[idx]
        else:
            return self.More_accurate(float(wavelength))
        
    def Remove(self):
        del self.intensity
        del self.wave

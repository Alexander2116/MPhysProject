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

def close_wave(wavelengths):
    ## Takes peaks at start of the acquised data set
    x = wavelengths
    xlen = len(x)
    potential_peaks = []
    for i in range(xlen-1):
        if x[i+1]-x[i] <= 0.03:
            potential_peaks.append(i+1)
    return potential_peaks


def remove_discontinuity(wavelength,intensity,x=3):
    """
    Parameters
    ----------
    x : int
        Indicates the range of spectra.
    1: 330nm-630nm

    Returns
        Intensity
    """
    # Peaks contain the LAST element of the data as well
    peaks = close_wave(change_type(wavelength))
    peaks.append(len(wavelength)-1)

    intensity = change_type(intensity)
    length_a = len(intensity)
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
        #print('Put the code different range')
        inten_d =[]
        # Positions start at 2033 entry [2032 position in the list], the next one is =+1014 till 8117
        ran = int((length_a - (length_a % 1019))/(1019))-1
        for j in range(ran):
            t = 1019 + j*1014 - 1
            inten_d.append(float(intensity_diff[t])+1.0)
            inten =sum(inten_d)
            for i in range(1014):
                #print(t+i+1)
                intensity[t+i+1] -= inten
        t += 1014
        k = len(intensity) - t
        inten_d.append(float(intensity_diff[t])+1.0)
        inten =sum(inten_d)
        for i in range(k-1):
            intensity[t+i+1] -= inten
            
    elif x==3:
        inten_d =[]
        jumps = peaks
        ranges = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]

        del jumps[-1]
        if (len(peaks))>1:
            # Positions start at 2033 entry [2032 position in the list], the next one is =+1014 till 8117
                for j in range(len(jumps)):
                    d = intensity[jumps[j]+2] - intensity[jumps[j]] # (i+2 - i+1) + (i+1 - i)
                    inten_d.append((float(intensity_diff[jumps[j]-1]) + d)/3)
                    inten = sum(inten_d)
                    for i in range(ranges[j]):
                        intensity[jumps[j]+i] -= inten
        #else:
            #Do nothing, there are no jumps
    else:
        print('Not defined, initial values returned')
    return intensity

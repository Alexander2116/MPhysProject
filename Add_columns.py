# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 12:35:26 2022

@author: Alex
"""

from pandas import read_csv
import pandas as pd
import numpy as np
import os.path
from os import listdir
import pandas
import statistics as st

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
    

def mean_intensity(data):
    number_column = len(data)
    mean_column = []
    std_list = []
    for i in range(len(data[0])):
        temp_mean = 0
        row = []
        for j in range(number_column-1):
            #temp_mean += data[j+1][i]
            row.append(data[j+1][i])
        temp_mean = sum(row)
        std = st.pstdev(row)
        mean_column.append(temp_mean/(number_column-1))
        std_list.append(std)
        
    return mean_column, std_list

def energy_deriv(data):
    energy = []
    for wavelength in data[0]:
        energy.append(1240/wavelength)
    return energy

def empty_col(data):
    empty_column = []
    for wavelength in data[0]:
        empty_column.append('')
    return empty_column

def remove_background(data,dark_data):
    clear_signal = []
    for i in range(len(data[1])):
        clear_signal.append(data[-2][i] - dark_data[i])
    return clear_signal

def direct_bandgap():
    return 0
    
def indirect_bandgap():
    return 0

def Planks_law(wavelength):
    # Spectral Radiance exitance
    lamb = wavelength/1000 # um
    T = 3000 # K
    h = 6.6256*10**(-34) # Js
    k = 1.3805*10**(-23) # J/K
    c = 2.99792*10**14 # um/s
    return 2*np.pi*h*c**2 / (lamb**5) * 1/(np.exp(h*c/(k*T*lamb))-1)

def Plank_spectrum(data):
    spec = []
    for wavelength in data[0]:
        spec.append(Planks_law(wavelength))
    return spec

def Spectral_norm(spectra_list):
    # Normalized Spectral Radiance
    # RESPONSE
    return [100*i/(spectra_list[-1]) for i in spectra_list]

def True_spectrum(measured,response):
    # NORMALISED INTENSITY
    # True PL spectrum after applying blackbody radiation
    # Data / response (spectral_norm, which is normalized Plank's Law)
    spec = []
    for i in range(len(measured)):
        spec.append(measured[i]/response[i])
    return spec

def half_value(data_column):
    return [i/2 for i in data_column]

def twice_value(data_column):
    return [2*i for i in data_column]


def __main__(PATH):
    """
    Creates new data columns in each csv file.
    Creates Energy column (hc/lambda) from column 0
    Creates Mean Intensity column from n next columns
    
    """
    input_path = PATH
    output_path = 'D:\\MPhys_data_modified'
    
    filenames = listdir(input_path)
    folder_list = [ filename for filename in filenames]
    
    for file in folder_list: # what day data was taken
        new_path = input_path + "\\" + file
        new_files = [filename for filename in listdir(new_path)]

        for file2 in new_files: # files in that day
            final_path = new_path + '\\' + file2
            final_output = output_path + '\\' + file2
            data = import_csv(final_path)
            create_csv(final_output)
                    
            ### MEAN INTENSITY  
            mean_int = mean_intensity(data)[0]
            mean_int_std = mean_intensity(data)[1]
            add_column(final_path,mean_int)
            add_column(final_path,mean_int_std)
            
            add_column2(final_output,data[0], 'wavelength [nm]')
            add_column2(final_output,mean_int, 'intensity')
            add_column2(final_output,mean_int_std, 'std of intensity')
                
            del data
            
        new_files.remove('dark.csv')
        
        dark_data_path = new_path + '\\' + 'dark.csv'
        dark_data = import_csv(dark_data_path)[-2]
        
        for file2 in new_files: # files in that day
            final_path = new_path + '\\' + file2
            final_output = output_path + '\\' + file2
            data = import_csv(final_path)
            
            ### REMOVE BACKGROUND
            removed_background = remove_background(data,dark_data)
            add_column(final_path,removed_background)
            add_column2(final_output,removed_background, 'Backgroundless I')
            
            ### Wavelength -> Energy
            add_column(final_path,empty_col(data))
            add_column(final_path,energy_deriv(data))
            add_column2(final_output,energy_deriv(data), 'eV')
            
            
            ### TRUE SPECTRUM
            add_column(final_path,empty_col(data))
            add_column(final_path,True_spectrum(removed_background,Spectral_norm(Plank_spectrum(data))))
            add_column2(final_output,True_spectrum(removed_background,Spectral_norm(Plank_spectrum(data))), 'True Spectrum')
            
            
            ### Half and twice data
            half_intensity = half_value(removed_background)
            twice_intensity = twice_value(removed_background)
            
            add_column2(final_output,empty_col(data))
            add_column2(final_output,half_intensity, 'I/2')
            add_column2(final_output,True_spectrum(half_intensity,Spectral_norm(Plank_spectrum(data))), 'True Spec / 2')
            
            add_column2(final_output,empty_col(data))
            add_column2(final_output,twice_intensity, '2I')
            add_column2(final_output,True_spectrum(twice_intensity,Spectral_norm(Plank_spectrum(data))), '2 True Spec')
            
            del data
        
        del dark_data

            
    return 0 #2D array




Mphys_path = 'D:\\MPhys'
__main__(Mphys_path)



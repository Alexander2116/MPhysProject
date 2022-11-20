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
import statistics as st
import Discontinuity_PL as DPL

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

def create_csv(path):
    with open(path, 'w') as file: 
        pass 
    file.close()
    
def add_column(path,data):
    # Add column to already existing csv file
    file = read_csv(path,header=None)
    file[len(file.columns)+1] = data
    file.to_csv(path,index=False,header=None)
    
    
def add_column2(path,data, column_name = ''):
    # Add column to csv file
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
    # Used in initial file
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
    # data = wavelength column
    energy = []
    for wavelength in data:
        energy.append(1240/float(wavelength))
    return energy

def empty_col(data):
    # Adds empty column to the data
    empty_column = []
    for wavelength in data:
        empty_column.append('')
    return empty_column

def remove_background(data,dark_data):
    # Data = intensity column
    clear_signal = []
    for i in range(len(data)):
        clear_signal.append(float(data[i]) - float(dark_data[i]))
    return clear_signal

def Planks_law(wavelength):
    # Spectral Radiance exitance
    lamb = float(wavelength)/1000 # um
    T = 3000 # K
    h = 6.6256*10**(-34) # Js
    k = 1.3805*10**(-23) # J/K
    c = 2.99792*10**14 # um/s
    return 2*np.pi*h*c**2 / (lamb**5) * 1/(np.exp(h*c/(k*T*lamb))-1)

def Plank_spectrum(data):
    # Data = wavelength
    spec = []
    for wavelength in data:
        spec.append(Planks_law(wavelength))
    return spec

def Spectral_norm(spectra_list):
    # Normalized Spectral Radiance
    # RESPONSE
    return [100*float(i)/(float(spectra_list[-1])) for i in spectra_list]

def True_spectrum(measured,response):
    # NORMALISED INTENSITY
    # True PL spectrum after applying blackbody radiation
    # Data / response (spectral_norm, which is normalized Plank's Law)
    spec = []
    for i in range(len(measured)):
        spec.append(float(measured[i])/float(response[i]))
    return spec

def half_value(data_column):
    # data_column = backgroundless intensity
    return [float(i)/2 for i in data_column]

def twice_value(data_column):
    # data_column = backgroundless intensity
    return [2*float(i) for i in data_column]


def __main__(PATH):
    """
    Creates new data columns in each csv file.
    Creates Energy column (hc/lambda) from column 0
    Creates Mean Intensity column from n next columns
    
    """
    import_path = PATH
    export_path = 'D:\\MPhys_data_modified_2'
    isExist = os.path.exists(export_path)
    
    if not isExist:
        os.makedirs(export_path)
    
    filenames = listdir(import_path)
    folder_list = [ filename for filename in filenames]
    
    for file in folder_list: # what day data was taken
        new_path = import_path + "\\" + file
        new_files = [filename for filename in listdir(new_path)]

        for file2 in new_files: # files in that day
            final_path = new_path + '\\' + file2
            final_output = export_path + '\\' + file2
            data = import_csv(final_path)
            create_csv(final_output)
                    
            ### MEAN INTENSITY  
            mean_int = mean_intensity(data)[0]
            mean_int_std = mean_intensity(data)[1]
            
            add_column2(final_output,data[0], 'wavelength [nm]')
            add_column2(final_output,mean_int, 'intensity')
            add_column2(final_output,mean_int_std, 'std of intensity')
                
            del data
            
        new_files.remove('dark.csv')
        
        dark_data_path = export_path + '\\' + 'dark.csv'
        dark_data = import_csv(dark_data_path,True)[1]
        
        for file2 in new_files: # files in that day
            final_output = export_path + '\\' + file2
            data = import_csv(final_output,True) # 0: Wavelength, 1: Intensity
            
            ### REMOVE BACKGROUND
            removed_background = remove_background(data[1],dark_data)
            #add_column(final_path,removed_background)
            add_column2(final_output,removed_background, 'Backgroundless I')
            
            ### REMOVE DISCONTINUITY
            removed_disc = DPL.remove_discontinuity(removed_background,1)
            del removed_background
            #add_column(final_path,removed_disc)
            add_column2(final_output,removed_disc, 'Continous I')
            
            ### Wavelength -> Energy
            #add_column(final_path,empty_col(data))
            #add_column(final_path,energy_deriv(data))
            add_column2(final_output,energy_deriv(data[0]), 'eV')
            
            
            ### TRUE SPECTRUM
            #add_column(final_path,empty_col(data))
            #add_column(final_path,True_spectrum(removed_disc,Spectral_norm(Plank_spectrum(data))))
            add_column2(final_output,True_spectrum(removed_disc,Spectral_norm(Plank_spectrum(data[0]))), 'True Spectrum')
            
            
            ### Half and twice data
            half_intensity = half_value(removed_disc)
            twice_intensity = twice_value(removed_disc)
            
            
            add_column2(final_output,empty_col(data[0]))
            add_column2(final_output,half_intensity, 'I/2')
            add_column2(final_output,True_spectrum(half_intensity,Spectral_norm(Plank_spectrum(data[0]))), 'True Spec / 2')
            
            add_column2(final_output,empty_col(data[0]))
            add_column2(final_output,twice_intensity, '2I')
            add_column2(final_output,True_spectrum(twice_intensity,Spectral_norm(Plank_spectrum(data[0]))), '2 True Spec')
            
            del half_intensity
            del twice_intensity
            del data
        
        del dark_data

            
    return 0 #2D array




Mphys_path = 'D:\\MPhys'
__main__(Mphys_path)



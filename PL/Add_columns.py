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
import Fit_function as BL

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
        result = float(data[i]) - float(dark_data[i])
        clear_signal.append(result)
            
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

def Bulb_spect(data, full_range = False):
    # Data = wavelength
    Bulb = BL.Bulb_spectra()
    if full_range == True:
        Bulb.Full_range() # Indicates that the range is 330-630
        print('yes')
    spec = []
    for lam in data:
        spec.append(Bulb.Spectra(float(lam)))
    del Bulb
    return spec

def Response(data, full_range = False):
    # Data = wavelength
    spec = []
    Bulb = Bulb_spect(data, full_range)
    Plank = Spectral_norm(data)
    for i in range(len(data)):
        spec.append(float(Bulb[i])/float(Plank[i]))
    return spec

def True_spectrum(Intensity, Wavelength, full_range = False):
    # NORMALISED INTENSITY
    # True PL spectrum after applying blackbody radiation
    # Intensity, Wavelength = Lists
    spec = []
    Resp = Response(Wavelength, full_range)
    for i in range(len(Intensity)):
        spec.append(float(Intensity[i])/float(Resp[i]))
    return spec

def half_value(data_column):
    # data_column = backgroundless intensity
    return [float(i)/2 for i in data_column]

def twice_value(data_column):
    # data_column = backgroundless intensity
    return [2*float(i) for i in data_column]

def remove_negative(data):
    clear_signal=[]
    for i in range(len(data)):
        result = float(data[i])
        # Replace negative values with 0
        if result < 0:
            clear_signal.append(0.001)
        else:
            clear_signal.append(result)
            
    return clear_signal

def __main__(PATH):
    """
    Creates new data columns in each csv file.
    Creates Energy column (hc/lambda) from column 0
    Creates Mean Intensity column from n next columns
    
    """
    import_path = PATH
    export_path = 'D:\\MPhys_data_modified'
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
            wavelength = data[0]
            ### REMOVE BACKGROUND
            removed_background = remove_background(data[1],dark_data)
            #add_column(final_path,removed_background)
            add_column2(final_output,removed_background, 'Backgroundless I')
            
            ### REMOVE DISCONTINUITY
            removed_disc = remove_negative(DPL.remove_discontinuity(wavelength,removed_background))

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
            add_column2(final_output,True_spectrum(removed_disc,data[0]), 'True Spectrum')
            
            """
            ### Half and twice data
            half_intensity = half_value(removed_disc)
            twice_intensity = twice_value(removed_disc)
            
            
            add_column2(final_output,empty_col(data[0]))
            add_column2(final_output,half_intensity, 'I/2')
            add_column2(final_output,True_spectrum(half_intensity,data[0]), 'True Spec / 2')
            
            add_column2(final_output,empty_col(data[0]))
            add_column2(final_output,twice_intensity, '2I')
            add_column2(final_output,True_spectrum(twice_intensity,data[0]), '2 True Spec')
            
            del half_intensity
            del twice_intensity
            """
            del data
        
        del dark_data

            
    return 0 #2D array




Mphys_path = 'D:\\PL_original_data'
__main__(Mphys_path)



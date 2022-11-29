# -*- coding: utf-8 -*-

import os.path
from os import listdir
from pandas import read_csv
import pandas as pd 


def create_csv(path):
    with open(path, 'w') as file: 
        pass 
    file.close()

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
    del temp_data
        
    file.to_csv(path,index=False,header=None)

def read_txt(path):
    f = open(path, "r")
    lines  = f.readlines()
    f.close()
    return lines

def write_txt(path,data):
    with open(path,'w') as f:
        f.writelines(data)
    f.close()

def select_extension(list_of_files,extension = '.txt'):
    # [s for s in list_of_files if any(xs in s for xs in extension)]
    return [s for s in list_of_files if extension in s]

def edit_data(data, indicators = ['','']):
    # Removes any details, leaves only the data column
    return_data = []
    position = 0
    data_len = len(data)
    
    ### Find First Data set ###
    for line in data:
        #print(line)
        position += 1
        if str(line) in indicators:
            break
        if position == data_len:
            break

    line = data[position]
    return_data.append(data[position-1])
    while line != "\n":
        return_data.append(line)
        position += 1
        if position == data_len:
            break
        else:
            line = data[position]
    ###################################
    ### If possible, find second Data set ###
    Break_Statement = False
    while Break_Statement == False:
        if position != data_len:
            for line in data[position : None]:
                position += 1
                if str(line) in indicators:
                    break
                if position == data_len:
                    Break_Statement = True
                    break
        else:
            Break_Statement = True
                
    while Break_Statement == False:
        line = data[position]
        return_data.append('\n')
        return_data.append(data[position-1])
        while line != "\n":
            return_data.append(line)
            position += 1
            if position == data_len:
                break
            else:
                line = data[position]
    ###################################
    return return_data

def __main__(load_data_path, export_data_path):

    isExist = os.path.exists(export_data_path)
    
    if not isExist:
        os.makedirs(export_data_path)

    filenames = listdir(load_data_path)

    s20 = select_extension(filenames, '.s20')
    s60 = select_extension(filenames, '.s60')
    dlt = select_extension(filenames, '.dlt')
    txt = select_extension(filenames, '.txt')
    ALL_FILES = [[s20,'.s20'],[s60,'.s60'],[dlt,'.dlt'],[txt,'.txt']]
    
    if not len(txt):
        del ALL_FILES[3]
    if not len(dlt):
        del ALL_FILES[2]
    if not len(s60):
        del ALL_FILES[1]
    if not len(s20):
        del ALL_FILES[0]

    indicators= ["!voltage, capacitance (pf),Conductance (S),W(m),Theta, Nd (/cc)\n","[Spectrum]\n",
                 "[data]\n",'!Voltage, Current\n']
    for file2 in ALL_FILES:
        for file in file2[0]:
            try:
                ext = file2[1]
                data_path = str(file)
                export_path = export_data_path +"\\"+ data_path.replace(ext,"_"+ext.replace('.','')+'.csv')
                import_path = load_data_path +"\\"+ data_path
                create_csv(export_path)
                data_temp = read_txt(import_path)
                data = edit_data(data_temp, indicators)
                del(data_temp)
                #read_file = pd.read_csv (r'C:\Users\Ron\Desktop\Test\Product_List.txt')
                write_txt(export_path,data)
            except:
                print("problem with file:  " + file)


Import = 'D:\\MPhys_DLTS\\SX5897A_C_1_5MeV'
Export = 'D:\\MPhys_DLTS\\SX5897A_Result'

__main__(Import,Export)
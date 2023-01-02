# -*- coding: utf-8 -*-

import os.path
from os import listdir
from pandas import read_csv
import pandas as pd 
import json



def read_txt(path):
    f = open(path, "r")
    lines  = f.readlines()
    f.close()
    return lines


class deal_json:
    PATH = '' ## PATH\\ FILE_NAME.JSON
    global temp_data
    
    def __init__(self,path):
        self.PATH = path
        
    def read(self):
        with open(self.PATH, "r") as file:
            return json.load(file)
            
    def create(self):
        with open(self.PATH, 'w') as fp:
            pass
        
    def update(self,entry):
        data = self.read()
        data.update(entry)
        self.write(data)
        
    def write(self,dictionary,indent=0):
        path = self.PATH
        if indent == 0:
            with open(path, "w") as outfile:
                json.dump(dictionary,outfile)
        else:
            # Serializing json
            json_object = json.dumps(dictionary, indent = indent)
            # Writing to sample.json
            with open(path, "w") as outfile:
                json.dump(json_object,outfile,indent=indent)
    

def select_extension(list_of_files,extension = '.txt'):
    # [s for s in list_of_files if any(xs in s for xs in extension)]
    return [s for s in list_of_files if extension in s]

def find_parameter(data,indicator):
    value = ''
    for line in data:
        if line.find(indicator) != -1:
            value = line.split('=')[-1]
            if value.find('\n'):
                value.replace('\n','')
            break
    return value

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

def remove_from_line(data):
    new_data_lines = []
    for line in data:
        new_data_lines.append(line.replace('\n',''))
    return new_data_lines

def separate_comma(data):
    d = [[] for x in range(len(data[0].split(',')))]
    for line in data:
        xx = line.split(',')
        for i in range(len(d)):
            d[i].append(xx[i])
        del xx
    return d
    
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
    extra_metadata = ['rate window']
    for file2 in ALL_FILES:
        for file in file2[0]:
            try:
                ext = file2[1]
                data_path = str(file)
                export_path = export_data_path +"\\"+ data_path.replace(ext,"_"+ext.replace('.','')+'.json')
                import_path = load_data_path +"\\"+ data_path
                JSS = deal_json(export_path)

                data_temp = read_txt(import_path)
                for em in extra_metadata:
                    xjson = {str(em) : float(find_parameter(data_temp, em))}
                    #xjson = "{%s : %i}" % (em,float(find_parameter(data_temp, em)))
                    JSS.write(xjson)
                    #write_json(export_path,xjson)
                data = edit_data(data_temp, indicators)
                del xjson
                
                data = remove_from_line(data)
                if data[0] == '[data]':
                    del data[0]
                    
                del(data_temp)
                xx = separate_comma(data)
                for i in range(len(xx)):
                    nkey = 'data'+str(i)
                    xjson = {nkey : xx[i]}
                    JSS.update(xjson)
                #read_file = pd.read_csv (r'C:\Users\Ron\Desktop\Test\Product_List.txt')
            except:
                print("problem with file:  " + file)


Import = 'D:\\MPhys_DLTS\\Test_E3'
Export = 'D:\\MPhys_DLTS\\JSON_E3'

__main__(Import,Export)
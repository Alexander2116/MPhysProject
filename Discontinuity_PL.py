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


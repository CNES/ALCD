#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys 
import os
import os.path as op
import otbApplication
import subprocess
import sqlite3
from osgeo import ogr
import numpy as np
from shutil import copyfile



class Legend_entry:
	opacity = 255
	color_name = ''
	def __init__(self, number, name, R,V,B):
		  self.name = name
		  self.R = R
		  self.V = V
		  self.B = B
		  self.number = number

def generate_qgis_table(classes):
	''' Generate a table color for qgis raster
	'''
	with open("qgis_table.txt", "w") as text_file:
		text_file.write("# Fichier d'exportation de palette de couleurs généré par QGIS")
		text_file.write("\n")
		text_file.write("INTERPOLATION:INTERPOLATED")
		text_file.write("\n")
		for cla in classes:
			text_file.write('{},{},{},{},{},{}\n'.format(cla.number, cla.R, cla.V, cla.B, cla.opacity, cla.name))
			
	
def generate_otb_table(classes):
	''' Generate a table color for OTB application
	'''
	with open("otb_table.txt", "w") as text_file:
		text_file.write("# Lines beginning with a # are ignored")
		text_file.write("\n")
		text_file.write("# class R G B")
		text_file.write("\n")
		for cla in classes:
			text_file.write('# {}\n{} {} {} {}\n'.format(cla.name, cla.number, cla.R, cla.V, cla.B))	

def define_dico():
	''' Define the color definition of each class here
	'''
	classes = []
	
	nullvalue = Legend_entry(0, 'null value', 195,255,42)
	nullvalue.color_name = 'yellow'
	
	background = Legend_entry(1, 'background', 187, 83, 58)
	background.color_name = 'brown'
	
	low_clouds = Legend_entry(2, 'low clouds', 210, 210, 210)
	low_clouds.color_name = 'light grey'

	high_clouds = Legend_entry(3, 'high clouds', 255, 123, 184)
	high_clouds.color_name = 'pink'
	
	clouds_shadows = Legend_entry(4, 'clouds shadows', 10, 10, 10)
	clouds_shadows.color_name = 'black'		

	land = Legend_entry(5, 'land', 0, 151, 56)
	land.color_name = 'green'	
	
	water = Legend_entry(6, 'water', 0, 142, 208)
	water.color_name = 'blue'	
	
	snow = Legend_entry(7, 'snow', 77, 77, 77)
	snow.color_name = 'dark grey'		
	
	classes = [nullvalue, background, low_clouds, high_clouds, clouds_shadows, land, water, snow]	
	print(len(classes))
	return classes
	
	
def main():
	classes = define_dico()
	generate_qgis_table(classes)
	generate_otb_table(classes)
	
if __name__=='__main__':
	main()		

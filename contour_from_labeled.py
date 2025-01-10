#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (contour_from_labeled.py)

Copyright© 2019 Centre National d’Etudes Spatiales

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 3
as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this program.  If not, see
https://www.gnu.org/licenses/gpl-3.0.fr.html
"""
import os
import os.path as op
import glob
import otbApplication
from osgeo import gdal
from PIL import Image
import numpy as np


def single_contour_from_labeled_dilatation(in_tif, out_tif, class_nb, radius=5, erode_before=True):
    ''' 
    Create a dilated contour of the given class
    '''
    class_nb = str(class_nb)
    # Extract the class
    ClassExtract = otbApplication.Registry.CreateApplication("BandMathX")
    ClassExtract.SetParameterStringList("il", [str(in_tif)])
    ClassExtract.SetParameterString("exp", "(im1b1 == {} ?  1 : 0)".format(class_nb))

    ClassExtract.UpdateParameters()
    ClassExtract.Execute()

    # Erode before allows to remove small elements of 1 pixel
    if erode_before:
        # Erosion
        Erosion = otbApplication.Registry.CreateApplication("BinaryMorphologicalOperation")
        Erosion.SetParameterInputImage("in", ClassExtract.GetParameterOutputImage("out"))
        Erosion.SetParameterString("filter", "erode")
        Erosion.SetParameterString("structype", "ball")
        Erosion.SetParameterInt("xradius", 1)
        Erosion.SetParameterInt("yradius", 1)
        Erosion.UpdateParameters()
        Erosion.Execute()

    # Dilatation
    Dilatation = otbApplication.Registry.CreateApplication("BinaryMorphologicalOperation")
    if erode_before:
        Dilatation.SetParameterInputImage("in", Erosion.GetParameterOutputImage("out"))
        radius += 1  # to compensate for the erosion
    else:
        Dilatation.SetParameterInputImage("in", ClassExtract.GetParameterOutputImage("out"))
    Dilatation.SetParameterString("filter", "dilate")
    Dilatation.SetParameterString("structype", "ball")
    Dilatation.SetParameterInt("xradius", radius)
    Dilatation.SetParameterInt("yradius", radius)
    Dilatation.UpdateParameters()
    Dilatation.Execute()

    # Substract the two
    Substract = otbApplication.Registry.CreateApplication("BandMathX")
    Substract.SetParameterString("out", str(out_tif))

    # The 1st band is the dilatation, the 2nd the original extracted class
    Substract.AddImageToParameterInputImageList("il", ClassExtract.GetParameterOutputImage("out"))
    Substract.AddImageToParameterInputImageList("il", Dilatation.GetParameterOutputImage("out"))
    Substract.SetParameterString("exp", "(im1b1 == im2b1 ?  0 : {}) ; (im1b1)".format(class_nb))
    Substract.UpdateParameters()
    Substract.ExecuteAndWriteOutput()

    return


def create_labelisation_contours(in_tif, out_tif, dilatation_radius=5, cloud_fusion=True):
    '''
    Create the contours of the labellisation image
    Dilatation radius is the dilatation of each contour

    in_tif is the labellised image (with classes 1,2,3,...)
    out_tif is the contours image
    '''
    # The classes that will be taken into account
    # /!\ The order is important, first is the most important and last the least
    # This order indicates that important contours override the below ones
    # ~ classes = [2,3,4,6,7,5]
    classes = [2, 3, 4, 7, 6]
    working_dir = op.dirname(in_tif)

    # Fuse the low clouds and high clouds classes, to make it more readable
    fused_in_tif = op.join(working_dir, 'fused_in_tif.tif')
    ClassFusion = otbApplication.Registry.CreateApplication("BandMathX")
    ClassFusion.SetParameterStringList("il", [str(in_tif)])
    ClassFusion.SetParameterString("out", str(fused_in_tif))
    if cloud_fusion:
        ClassFusion.SetParameterString("exp", "(im1b1 == 3 ?  2 : im1b1)")
    else:
        ClassFusion.SetParameterString("exp", "im1b1")
    ClassFusion.UpdateParameters()
    ClassFusion.ExecuteAndWriteOutput()

    temp_files = []
    # Create a dilatation mask for each class
    for class_nb in classes:
        temp_out_tif = op.join(working_dir, 'temp_{}.tif'.format(class_nb))
        temp_files.append(temp_out_tif)
        single_contour_from_labeled_dilatation(
            fused_in_tif, temp_out_tif, class_nb, radius=dilatation_radius)

    # Stack all the bands into one tif (with 2 bands, the 2nd being use for
    # the overwritting of the classes)
    for k in range(len(temp_files)):
        current_class = classes[k]
        StackingApp = otbApplication.Registry.CreateApplication("BandMathX")

        if k == 0:
            # first layer, so write directly the image
            in_temp_tif = temp_files[k]
            StackingApp.SetParameterStringList("il", [str(in_temp_tif)])
            StackingApp.SetParameterString("out", str(out_tif))
            StackingApp.SetParameterString("exp", "(im1b1) ; (im1b2)")
            StackingApp.UpdateParameters()
            StackingApp.ExecuteAndWriteOutput()
        else:
            # next layers, will write only the pixels not already written
            previous_tif = out_tif
            in_temp_tif = temp_files[k]
            StackingApp.SetParameterStringList("il", [str(previous_tif), str(in_temp_tif)])
            StackingApp.SetParameterString("out", str(out_tif))
            StackingApp.SetParameterString(
                "exp", "((im1b1 == 0 && im2b1 !=0 && im1b2 == 0) ? im2b1 : im1b1) ; im1b2 + im2b2")
            StackingApp.UpdateParameters()
            StackingApp.ExecuteAndWriteOutput()

    # Converts the 2 bands tif into a 1 band (drop the 2nd)
    MonoBand = otbApplication.Registry.CreateApplication("BandMathX")
    MonoBand.SetParameterStringList("il", [str(out_tif), str(in_tif)])
    MonoBand.SetParameterString("out", str(out_tif))
    MonoBand.SetParameterString("exp", "(im2b1 == 0 ? -1 : im1b1)")
    MonoBand.UpdateParameters()
    MonoBand.ExecuteAndWriteOutput()

    # Removes the useless temporary files
    temp_files.append(fused_in_tif)
    for temp in temp_files:
        try:
            os.remove(temp)
        except:
            print('Unable to remove {}'.format(temp))

    return


def rgb_contours_stacking(in_tif, contour_label_tif, out_png):
    '''
    Stacks the contour of the labeled image on the RGB image itself
    Easier for visualisation
    '''

    # in_tif is the bands stacking tiff
    ds = gdal.Open(in_tif)
    nb_bands = ds.RasterCount

    # temporary array to get the image characteristics
    temp_array = ds.GetRasterBand(1).ReadAsArray()
    image_width, image_height = temp_array.shape

    # select the RGB bands from tif and the thresholds above which
    # a 255 value will be assigned
    RGB_bands = [4, 3, 2]  # red, green, blue
    if nb_bands<3:
        RGB_bands = [1]
    RGB_thresholds = [2500, 2500, 2500]  # max thresholds

    # create the blank image
    rgbArray = np.zeros((image_width, image_height, 3), 'uint8')

    # load and rescale the different channels
    for channel, band in enumerate(RGB_bands):
        current_band = np.array(ds.GetRasterBand(band).ReadAsArray())
        current_band = np.divide(current_band, RGB_thresholds[channel]/255)
        current_band[current_band > 255] = 255.0

        rgbArray[..., channel] = current_band

    # save the RGB image in a png file
    img = Image.fromarray(rgbArray)
    img.save(op.join(op.dirname(out_png), 'quicklook.png'))

    # superimpose the labels on the current RGB array
    ds = gdal.Open(contour_label_tif)
    label_band = np.array(ds.GetRasterBand(1).ReadAsArray())
    label_band = label_band.astype(int)

    class_color = {}
    # New values for the colors
    class_color[-1] = [0., 0., 0.]  # null value
    class_color[1] = [187., 83., 58.]  # background
    class_color[2] = [0., 201., 13.]  # low clouds
    class_color[3] = [0., 180., 13.]  # high clouds
    class_color[4] = [255., 249., 55.]  # clouds shadows
    class_color[5] = [0., 151., 56.]  # land
    class_color[6] = [37., 106., 255.]  # water
    class_color[7] = [196., 86., 199.]  # snow

    # if the pixel belongs to a class on the contours labeled image,
    # its RGB value is overwritten on the RGB image value
    for class_nb in [-1, 1, 2, 3, 4, 5, 6, 7]:
        rgbArray[label_band == class_nb] = class_color[class_nb]

    # save the RGB image with contours in another png file
    img = Image.fromarray(rgbArray)
    img.save(out_png)

    return


def quick_contours(main_dir=''):
    '''
    Quick way to add the contours to an image
    '''
    raw_img = glob.glob(op.join(main_dir, 'In_data', 'Image', '*_bands.tif'))[0]

    labeled_tif = op.join(main_dir, 'Out', 'labeled_img_regular.tif')
    contour_tif = op.join(op.dirname(labeled_tif), 'contours_labels.tif')

    # Create the contours
    create_labelisation_contours(labeled_tif, contour_tif, dilatation_radius=4)

    # Create the quicklook png of the superimposition
    contour_superposed_png = op.join(op.dirname(labeled_tif), 'contours_superposition.png')
    rgb_contours_stacking(raw_img, contour_tif, contour_superposed_png)
    return
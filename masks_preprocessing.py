#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (masks_preprocessing.py)

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
import shutil
import os.path as op
from osgeo import ogr, gdal


import expand_point_region
import split_samples
import merge_shapefiles
import glob


def split_and_augment(global_parameters, k_fold_step=None, k_fold_dir=None):
    '''
    Split the 'merged.shp' file in two dataset
    Then augment the data
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    merged_shp = op.join(main_dir, 'Intermediate', global_parameters["general"]["merged_layers"])
    validation_shp = op.join(main_dir, 'Intermediate',
                             global_parameters["general"]["validation_shp"])
    training_shp = op.join(main_dir, 'Intermediate', global_parameters["general"]["training_shp"])
    validation_shp_extended = op.join(main_dir, 'Intermediate',
                                      global_parameters["general"]["validation_shp_extended"])
    training_shp_extended = op.join(main_dir, 'Intermediate',
                                    global_parameters["general"]["training_shp_extended"])

    if k_fold_step != None and k_fold_dir != None:
        # if not done before, create the split
        if k_fold_step == 0:
            K = global_parameters["training_parameters"]["Kfold"]
            split_samples.k_split(merged_shp, k_fold_dir, K)

        # copy directly the k fold
        load_kfold(training_shp, validation_shp, k_fold_step, k_fold_dir)

    else:
        # training proportion
        proportion = float(global_parameters["training_parameters"]["training_proportion"])

        # split into 2 datasets
        split_samples.split_points_sample(
            in_shp=merged_shp, train_shp=training_shp, validation_shp=validation_shp, proportion=proportion)

    # set the distance of the zone around each point
    max_dist_X = float(global_parameters["training_parameters"]["expansion_distance"])
    max_dist_Y = float(global_parameters["training_parameters"]["expansion_distance"])

    # the employed method is the squares one
    expand_point_region.create_squares(training_shp, training_shp_extended, max_dist_X, max_dist_Y)
    expand_point_region.create_squares(
        validation_shp, validation_shp_extended, max_dist_X, max_dist_Y)


def load_kfold(train_shp, validation_shp, k_fold_step, k_fold_dir):
    '''
    Copy the K train and validation shp to the default validation shp,
    in order to obtain the validation
    '''
    validation_files = glob.glob(op.join(k_fold_dir, 'validation*_k_*{}*'.format(k_fold_step)))
    train_files = glob.glob(op.join(k_fold_dir, 'train*_k_*{}*'.format(k_fold_step)))

    # Problem with the shapefiles is that they are accompagnied with
    # other files (prj, dbf, shx) that we should copy as well
    # so we go through all the names and copy them
    for valid_f in validation_files:
        # get the extension of the file
        _, extension = op.splitext(valid_f)
        dst_basename, _ = op.splitext(validation_shp)
        dst = dst_basename + extension
        shutil.copy(valid_f, dst)

    for train_f in train_files:
        # get the extension of the file
        _, extension = op.splitext(train_f)
        dst_basename, _ = op.splitext(train_shp)
        dst = dst_basename + extension
        shutil.copy(train_f, dst)


def rasterize_shp(input_shp, out_tif, reference_tif):
    '''
    From a shapefile, rasterize it
    '''
    gdalformat = 'GTiff'
    datatype = gdal.GDT_Byte
    burnVal = 0  # value for the output image pixels

    # Get projection info from reference image
    print(reference_tif)
    image = gdal.Open(reference_tif, gdal.GA_ReadOnly)

    # Open Shapefile
    shapefile = ogr.Open(input_shp)
    shapefile_layer = shapefile.GetLayer()

    # Rasterise
    output = gdal.GetDriverByName(gdalformat).Create(
        out_tif, image.RasterXSize, image.RasterYSize, 1, datatype, options=['COMPRESS=DEFLATE'])
    output.SetProjection(image.GetProjectionRef())
    output.SetGeoTransform(image.GetGeoTransform())

    # Write data to band 1
    band = output.GetRasterBand(1)
    band.SetNoDataValue(1)
    gdal.RasterizeLayer(output, [1], shapefile_layer, burn_values=[burnVal])

    # Close datasets
    band = None
    output = None
    image = None
    shapefile = None


def masks_preprocess(global_parameters, k_fold_step=None, k_fold_dir=None):
    '''
    Global preprocessing of the masks
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]

    layers_to_merge = []
    layers_classes = []

    # append the classes names and numbers
    for mask_name, mask_values in global_parameters["masks"].items():
        layers_to_merge.append(op.join(main_dir, 'In_data', 'Masks', mask_values["shp"]))
        layers_classes.append(mask_values["class"])

    merged_layers = op.join(main_dir, 'Intermediate', global_parameters["general"]["merged_layers"])

    print('  Merge the classes shapefiles into one')
    merge_shapefiles.merge_shapefiles(in_shp_list=layers_to_merge,
                                      class_list=layers_classes, out_shp=merged_layers)
    print('Done')

    if k_fold_step != None and k_fold_dir != None:
        print('  Copy the {}th dataset and augment the data'.format(k_fold_step))
    else:
        print('  Split into two datasets and augment the data')
    split_and_augment(global_parameters, k_fold_step=k_fold_step, k_fold_dir=k_fold_dir)
    print('Done')

    print('  Transform the no-data mask to raster')
    no_data_shp = op.join(main_dir, 'In_data', 'Masks',
                          global_parameters["general"]["no_data_mask"])
    no_data_tif = no_data_shp[0:-4] + '.tif'
    reference_tif = op.join(main_dir, 'In_data', 'Image',
                            global_parameters["user_choices"]["raw_img"])
    rasterize_shp(no_data_shp, no_data_tif, reference_tif)
    print('Done')

    return
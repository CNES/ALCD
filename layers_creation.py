#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (layers_creation.py)

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
from osgeo import ogr
from osgeo import gdal, osr
import L1C_band_composition
import subprocess
import tempfile

from alcd_params.params_reader import read_global_parameters


def empty_shapefile_creation(in_tif, out_shp_list, geometry_type='point'):
    ''' 
    Create empty shapefiles based on the SRS of the in_tif
    '''

    # get the projection and SRS
    ds = gdal.Open(r'{}'.format(in_tif))
    prj = ds.GetProjection()
    srs = osr.SpatialReference(wkt=prj)

    for k in range(len(out_shp_list)):
        out_shp = out_shp_list[k]

        outDriver = ogr.GetDriverByName("ESRI Shapefile")
        # Remove output shapefile if it already exists
        if os.path.exists(out_shp):
            outDriver.DeleteDataSource(out_shp)

        # Create the output shapefile
        outDataSource = outDriver.CreateDataSource(out_shp)
        if geometry_type == 'point':
            outLayer = outDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPoint)
        elif geometry_type == 'polygon':
            outLayer = outDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPolygon)
        else:
            print('Please enter a valid geometry type')
        # Add a class field
        classField = ogr.FieldDefn("class", ogr.OFTInteger)
        outLayer.CreateField(classField)

        # Close DataSource
        outDataSource.Destroy()

    return


def create_all_classes_empty_layers(global_parameters, force=False):
    '''
    Create all the empty layers files
    '''
    print('  Creation of the empty layers')
    main_dir = global_parameters["user_choices"]["main_dir"]

    # append from the configuration file the masks to create
    layers_to_create = []
    for mask_name, mask_values in global_parameters["masks"].items():
        layers_to_create.append(op.join(main_dir, 'In_data', 'Masks', mask_values["shp"]))

    in_tif = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    # check if they already exist
    if any([op.exists(f) for f in layers_to_create]) and force == False:
        print('Layers already present, use -force to erase and replace')
        return

    empty_shapefile_creation(in_tif, layers_to_create)

    # same for the no_data, but separate as it is a polygon type
    no_data_layer = [op.join(main_dir, 'In_data', 'Masks',
                             global_parameters["general"]["no_data_mask"])]
    empty_shapefile_creation(in_tif, no_data_layer, geometry_type='polygon')
    print('Done')


def populate_layer(in_shp, out_shp, x_coords, y_coords):
    '''
    Populate a layer with points from their geo coordinates
    '''
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(in_shp, 0)
    inLayer = inDataSource.GetLayer()

    srs = inLayer.GetSpatialRef()

    # Save extent to a new Shapefile
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    # Remove output shapefile if it already exists
    if os.path.exists(out_shp):
        outDriver.DeleteDataSource(out_shp)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(out_shp)
    outLayer = outDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPoint)

    # Add a class field
    classField = ogr.FieldDefn("class", ogr.OFTInteger)
    outLayer.CreateField(classField)

    # Create the feature and set values
    for point_nb in range(len(x_coords)):
        # set the location of the point
        point = ogr.Geometry(ogr.wkbPoint)
        point.SetPoint(0, x_coords[point_nb], y_coords[point_nb])

        featureDefn = outLayer.GetLayerDefn()
        feature = ogr.Feature(featureDefn)
        feature.SetGeometry(point)
        outLayer.CreateFeature(feature)

    # Close DataSource
    inDataSource.Destroy()
    outDataSource.Destroy()

    return


def create_no_data_shp(global_parameters,paths_parameters, force=False):
    '''
    Create automatically polygons overs the no_data pixels
    in both the clear and cloudy date
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]

    tmp_name = next(tempfile._get_candidate_names())
    tmp_tif = op.join('tmp', 'no_data_mask_{}.tif'.format(tmp_name))

    # Create the temporary no data TIF
    L1C_band_composition.create_no_data_tif(global_parameters,paths_parameters, tmp_tif)

    # polygonize the raster
    print("  Polygonization")
    tmp_shp = op.join('tmp', 'no_data_mask_{}.shp'.format(tmp_name))
    out_layer = 'no_data_shape'
    command = 'gdal_polygonize.py {} -mask {} -f "ESRI Shapefile" {} {} class'.format(
        tmp_tif, tmp_tif, tmp_shp, out_layer)
    subprocess.call(command, shell=True)

    # simplify the polygons
    out_shp = op.join(main_dir, 'In_data', 'Masks', 'no_data.shp')
    simplify_geometry(tmp_shp, out_shp, tolerance=100)
    return


def simplify_geometry(in_shp, out_shp, tolerance=100):
    ''' Simplification of a shapefile
    This allows to have lighter polygons, enhancing the rapidty
    '''
    print("  Geometry simplification")
    command = "ogr2ogr {} {} -simplify {}".format(out_shp, in_shp, str(tolerance))
    subprocess.call(command, shell=True)
    print("Done")


def main():
    global_parameters = read_global_parameters(op.join('parameters_files', 'global_parameters.json'))

    create_all_classes_empty_layers(global_parameters, force=False)

    create_no_data_shp(global_parameters)

    return


if __name__ == '__main__':
    main()

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (merge_shapefiles.py)

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


def merge_shapefiles(in_shp_list, class_list, out_shp):
    ''' 
    Create a merged shapefile
    The class_list should be in the same order than the in_shp_list 
    '''

    for k in range(len(in_shp_list)):
        print(in_shp_list)
        in_shp = in_shp_list[k]
        current_class = class_list[k]

        inDriver = ogr.GetDriverByName("ESRI Shapefile")
        inDataSource = inDriver.Open(in_shp, 0)
        inLayer = inDataSource.GetLayer()

        srs = inLayer.GetSpatialRef()

        if k == 0:
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
        for point in inLayer:
            ingeom = point.GetGeometryRef()

            featureDefn = outLayer.GetLayerDefn()
            feature = ogr.Feature(featureDefn)
            feature.SetGeometry(ingeom)
            feature.SetField("class", current_class)
            outLayer.CreateFeature(feature)

        # Close DataSource
        inDataSource.Destroy()
    outDataSource.Destroy()
    return
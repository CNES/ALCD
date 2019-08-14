#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (expand_point_region.py)

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
import sys
import os
import os.path as op
import subprocess
import ogr
import numpy as np


def compute_polygon(point, dist_X, dist_Y, out_layer):
    '''
    For each point, a square is computed from dist_X
    and dist_Y in each direction.
    '''

    ingeom = point.GetGeometryRef()

    Xpoint = ingeom.GetX(0)
    Ypoint = ingeom.GetY(0)

    # definition of the square sides
    left = Xpoint-dist_X
    right = Xpoint + dist_X
    top = Ypoint+dist_Y
    bottom = Ypoint-dist_Y

    border = ogr.Geometry(ogr.wkbLinearRing)
    # 4 corners, needs to be closed with the 5th point
    border.AddPoint(left, top)
    border.AddPoint(right, top)
    border.AddPoint(right, bottom)
    border.AddPoint(left, bottom)
    border.AddPoint(left, top)

    # create the polygon
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(border)

    # assign the class and expand status
    featureDefn = out_layer.GetLayerDefn()
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry(poly)

    current_class = point.GetField("class")
    feature.SetField("class", current_class)
    expand_status = point.GetField("expand")
    feature.SetField("expand", expand_status)
    out_layer.CreateFeature(feature)


def create_squares(in_shp, out_shp, max_dist_X, max_dist_Y, half_res_X, half_res_Y):
    ''' 
    Create a neighbourhoud around all the points in a shapefile
    For each point, a square around it is created, from -max_dist to +max_dist
    in each direction
    '''
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(in_shp, 0)
    inLayer = inDataSource.GetLayer()

    srs = inLayer.GetSpatialRef()

    # Watch out : sometimes the unit is meter, sometimes degree
    srs_unit = srs.GetAttrValue('unit')

    if srs_unit == 'Meter':
        print('Unit is meter, no change')
    elif srs_unit == 'Degree':
        print('Unit is degree, needs to be converted')

    # Save extent to a new Shapefile
    outDriver = ogr.GetDriverByName("ESRI Shapefile")

    # Remove output shapefile if it already exists
    if os.path.exists(out_shp):
        outDriver.DeleteDataSource(out_shp)

    # Create the output shapefile
    outDataSource = outDriver.CreateDataSource(out_shp)
    outLayer = outDataSource.CreateLayer("buff_layer", srs, geom_type=ogr.wkbPolygon)

    # Add a class field
    classField = ogr.FieldDefn("class", ogr.OFTInteger)
    outLayer.CreateField(classField)
    print('{} squares will be created'.format(len(inLayer)))

    # Add an expand field
    expandField = ogr.FieldDefn("expand", ogr.OFTInteger)
    expandField.SetSubType(ogr.OFSTBoolean)
    outLayer.CreateField(expandField)

    # Create the feature and set values
    for point in inLayer:
        current_class = point.GetField("class")
        expand_status = point.GetField("expand")

        if current_class != None and expand_status == True:
            compute_polygon(point, max_dist_X, max_dist_Y, outLayer)

        # Add points with no expand computed
        elif current_class != None and expand_status == False:
            compute_polygon(point, half_res_X, half_res_Y, outLayer)

    # Close DataSource
    inDataSource.Destroy()
    outDataSource.Destroy()

    return


def main():
    in_shp = '/mnt/data/home/baetensl/classification_clouds/Data/Orleans_all/In_data/Masks/land.shp'
    out_shp = '/mnt/data/home/baetensl/classification_clouds/Data/Orleans_all/In_data/Masks/SQUARES.shp'

    create_squares(in_shp, out_shp, max_dist_X=100, max_dist_Y=100)


if __name__ == '__main__':
    main()

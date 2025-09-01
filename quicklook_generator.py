#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (quicklook_generator.py)

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
import argparse

import find_directory_names
from alcd_params.params_reader import read_paths_parameters


def create_jpg(in_jp2s, out_jpg):
    ''' 
    Create empty shapefiles based on the SRS of the in_tif
    '''
    bands_text = ''
    for band in in_jp2s:
        bands_text = bands_text + ' ' + band

    # Create the VRT
    tempVRT = str('tmp/temp_vrt.vrt')
    build_vrt = 'gdalbuildvrt -separate {} {} '.format(tempVRT, bands_text)
    os.system(build_vrt)

    # Create the JPG
    translate = 'gdal_translate -of JPEG -outsize 800 0 -scale 0 2500 -ot byte '+tempVRT + ' ' + out_jpg

    os.system(translate)

    return


def create_all_quicklook(location, out_dir, paths_parameters):
    '''
    Create all the quicklooks for a given location
    '''
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    all_dates = find_directory_names.get_all_dates(location, paths_parameters)
    nb_total_dates = len(all_dates)
    k = 0
    for current_date in all_dates:
        print('{}/{} dates done'.format(k, nb_total_dates))
        try:
            L1C_dir, band_prefix, date = find_directory_names.get_L1C_dir(
                location, current_date, paths_parameters, display=True)
        except Exception as e:
            print(e)
            k += 1
            pass

        R = op.join(L1C_dir, (band_prefix + '04.jp2'))
        G = op.join(L1C_dir, (band_prefix + '03.jp2'))
        B = op.join(L1C_dir, (band_prefix + '02.jp2'))
        in_jp2s = [R, G, B]

        out_jpg = op.join(out_dir, (location+'_'+date+'.jpg'))
        create_jpg(in_jp2s, out_jpg)

        k += 1


def getarguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', action='store', default=None, dest='locations',
                        help='Locations, needs to be separated by a comma (e.g. "-l Arles,Gobabeb,Orleans")')
    parser.add_argument('-paths_parameters', dest='paths_parameters_file',
                        help='str, path to json file which contain useful path for ALCD', required=True)

    results = parser.parse_args()
    return vars(results)

def quicklook_generator(locations=None, paths_parameters_file=None):
    locations_to_parse = locations
    paths_parameters = read_paths_parameters(paths_parameters_file)
    if locations_to_parse != None:
        loc = locations_to_parse.split(',')

    else:
        loc = ['Mongu', 'Gobabeb', 'RailroadValley', 'Arles', 'Marrakech']
        loc = ['Alta_Floresta_Brazil']

    for location in loc:
        out_dir = op.join('tmp', location)
        create_all_quicklook(location, out_dir, paths_parameters)

    return

def main():
    """
    It parses the command line arguments and calls the all_run_alcd function.
    """
    args = getarguments()
    quicklook_generator(**args)


if __name__ == '__main__':
    main()
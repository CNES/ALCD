#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (find_directory_names.py)

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
import json
import glob
import argparse
import re
import csv


def get_all_dates(location, paths_parameters):
    ''' 
    Get all dates for a given location
    '''
    L1C_dir = paths_parameters["global_chains_paths"]["L1C"]
    location_dir = op.join(L1C_dir, location)
    all_dates_dir = glob.glob(op.join(location_dir, 'S2*.SAFE'))
    dates = []
    for date_dir in all_dates_dir:
        last_dir = op.basename(op.normpath(date_dir))

        # DEPRECATED : that was used before, but doesnt work for
        # dates before 2016
        # ~ start_date_index = last_dir.index('_20') # get a string begining by _20, which should be the date
        # a date has 8 characters

        # Regex allows this to work better. In fact, there is 2 dates in
        # the dates before 2016
        for m in re.finditer('_20[0-9]{6}', last_dir):
            start_date_index = m.start()
            dates.append(last_dir[start_date_index+1:start_date_index+9])

    dates = sorted(dates)
    return dates


def is_valid_date(location, current_date, paths_parameters):
    '''
    Check if a date is valid for a given location
    '''
    valid_dates = sorted(get_all_dates(location, paths_parameters))
    if current_date in valid_dates:
        return True
    else:
        return False


def get_closest_dates(location, current_date, mode='after', nb_days=1):
    ''' Returns the closest valid dates to the given date
    They could be before or after.
    If the mode is 'after' and the given date is valid, it will appear in
    the returned list, unlike in the 'before' mode 
    '''

    valid_dates = sorted(get_all_dates(location))

    # copy the list
    all_dates = list(valid_dates)
    all_dates.append(current_date)
    all_dates = sorted(all_dates)

    current_date_index = all_dates.index(current_date)

    closest_dates = []

    if mode == 'before':
        closest_dates = valid_dates[current_date_index-nb_days:current_date_index]
    elif mode == 'after':
        closest_dates = valid_dates[current_date_index:current_date_index+nb_days]
    else:
        print('Choose a valid mode')

    return closest_dates


def get_L1C_dir(location, wanted_date, paths_parameters, display=True):
    '''
    Get the path of the L1C directory
    If the date is not valid, returns the closest one (after)
    '''
    L1C_dir = paths_parameters["global_chains_paths"]["L1C"]
    location_dir = op.join(L1C_dir, location)

    date = wanted_date

    with_date = glob.glob(op.join(location_dir, 'S2*_{}*.SAFE'.format(date)))
    granule = op.join(with_date[0], 'GRANULE')

    final = glob.glob(op.join(granule, '*', 'IMG_DATA'))[0]
    if display == True:
        print('----- L1C directory -----')
        print(final)
        print(date)

    # name prefix for any band
    band_prefix = op.basename(glob.glob(op.join(final, '*_B*.jp2'))[0])[0:-6]

    if display == True:
        sub_files = glob.glob(op.join(final, '*.jp2'))
        for image_name in sub_files:
            file_name = op.basename(op.normpath(image_name))
            print(file_name)

    return final, band_prefix, date
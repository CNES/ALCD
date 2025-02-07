#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (synthese_alcd_runs.py)

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
import json
import csv
import os.path as op
from pprint import pprint
import numpy as np
import os
import shutil
import matplotlib.pyplot as plt
import glob

import otbApplication
from matplotlib.lines import Line2D

from alcd_params.params_reader import read_paths_parameters


def get_main_directories(paths_configuration, locations, excluded):
    Data_ALCD_dir = paths_configuration["data_paths"]["data_alcd"]
    main_dirs = []
    excluded_dirs = []
    for wrong_dir in excluded:
        excluded_dirs.extend(glob.glob(op.join(Data_ALCD_dir, '*' + wrong_dir + '*')))
    for location in locations:
        main_dirs.extend(glob.glob(op.join(Data_ALCD_dir, '*' + location + '*')))

    for k in range(len(excluded_dirs)):
        try:
            main_dirs.remove(excluded_dirs[k])
        except:
            pass

    return main_dirs


def compute_samples_evolution_statistics(main_dirs):
    nb_sites = len(main_dirs)
    nb_iterations = []
    short_names = [op.basename(d) for d in main_dirs]

    points_numbers = []
    for n in range(nb_sites):
        previous_iter_dir = op.join(main_dirs[n], 'Previous_iterations')

        # Count the number of previous iterations
        all_potential_saves = os.listdir(previous_iter_dir)
        all_saves = []
        for a in all_potential_saves:
            if 'SAVE' in op.basename(a):
                all_saves.append(a)

        # Count the number of samples for each iteration
        nb_points = []
        print(short_names[n])
        for a in all_saves:
            mask_path = op.join(previous_iter_dir, a, 'In_data', 'Masks')
            nb_points.append(count_points_in_dir(mask_path))

        # add the ones of the final iteration or not ??? (should be in the last SAVE normally)

        points_numbers.append(nb_points)

    ordered = points_numbers[:]
    ordered.sort()

    k = 0
    for p in points_numbers:
        ordered = p[:]
        ordered.sort()

        if p != ordered:
            print('Not normal: {}'.format(short_names[k]))
            print(ordered)
            print(p)
        k += 1

    for k in range(len(points_numbers)):
        points_numbers[k] = list(set(points_numbers[k]))
        points_numbers[k].sort()
        print(short_names[k])
        print(points_numbers[k])

    print(points_numbers[2])

    nb_iterations = [len(p) for p in points_numbers]

    # Extend all the arrays to have the same number of iterations
    max_nb_of_iter = max(nb_iterations)
    for k in range(len(points_numbers)):
        diff_with_max = max_nb_of_iter - len(points_numbers[k])
        if diff_with_max > 0:
            points_numbers[k] = np.append(points_numbers[k], np.repeat(
                points_numbers[k][-1], diff_with_max))

    return nb_iterations, points_numbers


def plot_samples_evolution_statistics(main_dirs):
    nb_iterations, points_numbers = compute_samples_evolution_statistics(main_dirs)

    iterations_stats = [np.mean(nb_iterations), np.std(nb_iterations)]
    last_points_numbers = [p[-1] for p in points_numbers]
    last_points_numbers_stats = [np.mean(last_points_numbers), np.std(last_points_numbers)]
    points_numbers_stats = [np.mean(points_numbers, axis=0), np.std(points_numbers, axis=0)]

    print(iterations_stats)
    print(points_numbers_stats)

    fig, ax = plt.subplots()
    ax.yaxis.grid(True)  # put horizontal grid

    for k in range(len(points_numbers)):
        plt.plot(range(len(points_numbers[k])), points_numbers[k], 'o-', alpha=0.1, color='k')

    plt.errorbar(range(len(points_numbers_stats[0])), points_numbers_stats[0], points_numbers_stats[1], linestyle='-',
                 marker='o', lw=2, elinewidth=2, capsize=8, capthick=1, color='g')

    plt.xlabel('Iteration')
    plt.ylabel('Number of samples')
    plt.title("Statistics on {} scenes \n Mean number of iterations = {:.01f} +- {:.01f}".format(
        len(main_dirs), iterations_stats[0], iterations_stats[1]))

    # Custom legend
    custom_lines = []
    custom_lines.append(Line2D([0], [0], marker='o', alpha=0.1, color='k'))
    custom_lines.append(Line2D([0], [0], marker='o', alpha=1, color='g'))

    legend_labels = ['Evolution per scene', 'Mean and std of all scenes']

    plt.legend(custom_lines, legend_labels, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

    plt.show(block=False)

    out_fig = op.join('tmp_report', 'samples_for_iterations.png')
    plt.savefig(out_fig, bbox_inches='tight')


def count_points_in_shp(in_shp):
    ''' 
    Count the points number in a shp
    '''
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(in_shp, 0)
    inLayer = inDataSource.GetLayer()

    nb_points = len(inLayer)

    inDataSource.Destroy()
    return nb_points


def count_points_in_dir(directory):
    '''
    Count the points number in all the specified shp in a directory
    '''
    shp_names = ['background.shp', 'land.shp', 'low_clouds.shp', 'high_clouds.shp', 'clouds_shadows.shp',
                 'land.shp', 'water.shp', 'snow.shp']

    full_paths = [op.join(directory, shp) for shp in shp_names]
    nb_points = []
    for fil in full_paths:
        nb_points.append(count_points_in_shp(fil))
    total_points = sum(nb_points)

    return total_points


def mean_confidence(confidence_tif):
    '''
    Compute the mean confidence of an iteration from the confidence map
    '''
    ComputeImagesStatistics = otbApplication.Registry.CreateApplication("ComputeImagesStatistics")
    ComputeImagesStatistics.SetParameterStringList("il", ['QB_1_ortho.tif'])
    ComputeImagesStatistics.SetParameterString("out", "EstimateImageStatisticsQB1.xml")
    ComputeImagesStatistics.ExecuteAndWriteOutput()


def main():
    paths_configuration = read_paths_parameters(op.join('parameters_files', 'paths_configuration.json'))

    locations = ['Arles', 'Orleans', 'Gobabeb', 'RailroadValley',
                 'Pretoria', 'Mongu', 'Ispra', 'Marrakech']
    excluded = ['Gobabeb_*_20171014', 'Mongu_*_20171013']
    excluded = ['Arles_31TFJ_20171221', 'Gobabeb_33KWP_20161221',
                'Pretoria_35JPM_20171014', 'Gobabeb_33KWP_20171014']
    excluded = ['Gobabeb_33KWP_20171014']
    excluded = []
    plot_type = 'boxplot'
    plot_type = 'errorbar'

    main_dirs = get_main_directories(paths_configuration, locations, excluded)
    #~ compute_statistics(main_dirs)

    plot_samples_evolution_statistics(main_dirs)


if __name__ == '__main__':
    main()

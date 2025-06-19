#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (all_run_alcd.py)

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
import json
import shutil
import argparse
import tempfile

import OTB_workflow
import masks_preprocessing
import layers_creation
import L1C_band_composition
import OTB_workflow as OTB_wf
import metrics_exploitation
import find_directory_names
import confidence_map_exploitation

from alcd_params.params_reader import read_global_parameters, read_models_parameters, read_paths_parameters


def initialization_global_parameters(main_dir, data, paths_configuration, raw_img_name, location, current_date, clear_date):
    ''' To initialize the path and name in the JSON file
    Must be done at the very beggining
    '''

    # Working with buffered content
    data["user_choices"]["main_dir"] = main_dir
    data["user_choices"]["raw_img"] = raw_img_name
    data["user_choices"]["current_date"] = current_date
    data["user_choices"]["clear_date"] = clear_date
    data["user_choices"]["location"] = location
    data["user_choices"]["tile"] = paths_configuration["tile_location"][location]
    return data


def invitation_to_copy(global_parameters, first_iteration=False):
    '''
    Used if the user is working on 2 machines, to simplify his task
    It will print automatically the command to enter in the terminal
    Will also save the current iteration in a directory
    '''
    print('------USER ACTION REQUIRED------')

    if first_iteration == False:
        print('------DO YOU WANT TO DO ANOTHER ITERATION ?------')

        # save the folders
        main_dir = global_parameters["user_choices"]["main_dir"]
        previous_iterations_dir = op.join(main_dir, 'Previous_iterations')

        k = 0
        while op.exists(op.join(previous_iterations_dir, 'SAVE_{}'.format(k))):
            k += 1
        os.makedirs(op.join(previous_iterations_dir, 'SAVE_{}'.format(k)))
        print('SAVE_{} directory created'.format(k))

        save_dir = op.join(previous_iterations_dir, 'SAVE_{}'.format(k))

        # Enter which dirs you want to save
        # Not all so it doesnt take too much disk space
        dirs_to_copy = ['In_data/Masks', 'Statistics', 'Samples', 'Models', 'Out']
        for directory in dirs_to_copy:
            src = op.join(main_dir, directory)
            dst = op.join(save_dir, directory)
            shutil.copytree(src, dst)

        # destroy the folders with K-fold for the current iteration
        statistics_dir = op.join(main_dir, 'Statistics')
        k = 0
        while op.exists(op.join(statistics_dir, 'K_fold_{}'.format(k))):
            shutil.rmtree(op.join(statistics_dir, 'K_fold_{}'.format(k)))
            k += 1

def run_all(part, global_parameters, paths_parameters, model_parameters, first_iteration=False, location=None, wanted_date=None, clear_date=None, k_fold_step=None, k_fold_dir=None, force=False):

    if part == 1:
        # Define the main parameters for the algorithm
        # If all is filled, will update the JSON file
        if location != None and wanted_date != None and clear_date != None:

            Data_ALCD_dir = paths_parameters["data_paths"]["data_alcd"]

            tile = paths_parameters["tile_location"][location]
            if find_directory_names.is_valid_date(location, wanted_date, paths_parameters):
                current_date = wanted_date
            else:
                print('Error: please enter a valid wanted date')
                raise NameError('Invalid wanted date')

            if not find_directory_names.is_valid_date(location, clear_date, paths_parameters):
                print('Error: please enter a valid cloud free date')
                raise NameError('Invalid cloud free date')
            main_dir = op.join(Data_ALCD_dir, (location + '_' + tile + '_' + current_date))
            raw_img_name = location + "_bands.tif"

            # Initialize the parameters with them
            global_parameters = initialization_global_parameters(
                main_dir, global_parameters, paths_parameters, raw_img_name, location, current_date, clear_date)

            if first_iteration == True:
                # Create the directories
                OTB_workflow.create_directories(global_parameters)

                # Copy the global_parameters files to save it
                src = global_parameters["json_file"]
                dst = op.join(global_parameters["user_choices"]
                              ["main_dir"], 'In_data', 'used_global_parameters.json')
                shutil.copyfile(src, dst)

                # Create the images .tif and .jp2, i.e. the features
                L1C_band_composition.create_image_compositions(
                    global_parameters, location, paths_parameters, current_date, heavy=True, force=force)

                # Create the empty layers
                layers_creation.create_all_classes_empty_layers(global_parameters, force=force)

                # Fill automatically the no_data layer from the L1C missing
                # pixels
                layers_creation.create_no_data_shp(global_parameters,paths_parameters, force=force)
    # ----------------------------------------------
    # WAIT FOR USER MODIFICATION OF THE LAYERS IN LOCAL
    # ----------------------------------------------

    elif part == 2:
        # Merge the layers, split in training and validation data, augment the data
        if k_fold_step == None or k_fold_dir == None:
            masks_preprocessing.masks_preprocess(global_parameters)
        else:
            masks_preprocessing.masks_preprocess(global_parameters, k_fold_step, k_fold_dir)

    elif part == 3:
        # Compute the statistics of the image and samples, and extract the later
        if first_iteration == True:
            # needs to be done only once
            OTB_wf.compute_image_stats(global_parameters)

        proceed = True
        OTB_wf.compute_samples_stats(global_parameters, proceed=True)
        OTB_wf.select_samples(global_parameters, strategy="constant_8000")
        OTB_wf.extract_samples(global_parameters, proceed=proceed)

    elif part == 4:
        # Train the model and classify the image
        OTB_wf.train_model(global_parameters, model_parameters, shell=False, proceed=True)
        additional_name = ''
        OTB_wf.image_classification(global_parameters, shell=False,
                                    proceed=True, additional_name=additional_name)
        OTB_wf.confidence_map_viz(global_parameters, additional_name=additional_name)
        # regularization_radius in pixel
        regularization_radius = int(
            global_parameters["training_parameters"]["regularization_radius"])
        OTB_wf.classification_regularization(
            global_parameters, proceed=True, radius=regularization_radius)

    elif part == 5:
        # Compute some metrics
        OTB_wf.compute_mat_conf(global_parameters)
        OTB_wf.fancy_classif_viz(global_parameters, proceed=True)
        try:
            confidence_map_exploitation.compute_all_confidence_stats(global_parameters)
            confidence_map_exploitation.plot_confidence_evolution(global_parameters)
            confidence_map_exploitation.plot_samples_evolution(global_parameters)
        except:
            pass
        metrics_exploitation.get_model_metrics(global_parameters)
        metrics_exploitation.save_model_metrics(global_parameters)
        metrics_exploitation.retrieve_Kfold_data(global_parameters)

    elif part == 6:
        # Create the contours for a better visualisation
        OTB_wf.create_contour_from_labeled(global_parameters, proceed=True)


def str2bool(v):
    '''
    Use it to change multiple pseudo-boolean values to a real boolean
    '''
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    # parsing from the shell
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', action='store', default=None,
                        dest='first_iteration', help='Bool, is it the first iteration?')
    parser.add_argument('-s', action='store', type=int, default=-1, dest='user_input',
                        help='Int, The step: 0 to modify the masks, 1 to run the algorithm')
    parser.add_argument('-l', action='store', default=None,
                        dest='location', help='Location (e.g. Orleans)')
    parser.add_argument('-d', action='store', default=None, dest='wanted_date',
                        type=str, help='Date, The desired date to process (e.g. 20170702)')
    parser.add_argument('-c', action='store', default=None, dest='clear_date',
                        help='Date, The nearest clear date (e.g. 20170704)')
    parser.add_argument('-dates', action='store', default='false',
                        dest='get_dates', help='Bool, Get the available dates')
    parser.add_argument('-kfold', action='store', default='false',
                        dest='kfold', help='Bool, Do a K-fold cross validation')
    parser.add_argument('-force', action='store', default='false', dest='force',
                        help='Bool, Force ALCD to erase previous In_Data')
    parser.add_argument('-global_parameters', dest='global_parameters_file',
                        help='str, path to json file which parametrize ALCD', required=True)
    parser.add_argument('-paths_parameters',dest='paths_parameters_file',
                        help='str, path to json file which contain useful path for ALCD', required=True)
    parser.add_argument('-model_parameters', dest='model_parameters_file',
                        help='str, path to json file which contain classifier parameters', required=True)
    results = parser.parse_args()
    location = results.location
    global_parameters = read_global_parameters(results.global_parameters_file)
    paths_parameters = read_paths_parameters(results.paths_parameters_file)
    model_parameters = read_models_parameters(results.model_parameters_file)

    global_parameters["json_file"] = results.global_parameters_file
    get_dates = str2bool(results.get_dates)
    if get_dates:
        available_dates = find_directory_names.get_all_dates(location, paths_parameters)
        print('\nAvailable dates:\n')
        print([str(d) for d in available_dates])
        return

    if results.first_iteration == None:
        print('Please enter a boolean for the first iteration')
        return
    else:
        first_iteration = str2bool(results.first_iteration)

    if results.user_input == None:
        print('Please enter an integer for the step')
        return
    else:
        user_input = results.user_input

    wanted_date = results.wanted_date
    clear_date = results.clear_date
    force = str2bool(results.force)
    kfold = str2bool(results.kfold)

    if kfold:
        tmp_name = next(tempfile._get_candidate_names())
        k_fold_dir = op.join('tmp', 'kfold_{}'.format(tmp_name))
        if not op.exists(k_fold_dir):
            os.makedirs(k_fold_dir)
            print(k_fold_dir + ' created')

        K = int(global_parameters["training_parameters"]["Kfold"])
        for k_fold_step in range(K):
            run_all(part=2, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                    first_iteration=first_iteration, k_fold_step=k_fold_step, k_fold_dir=k_fold_dir)
            run_all(part=3, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                    first_iteration=first_iteration, k_fold_step=k_fold_step, k_fold_dir=k_fold_dir)
            run_all(part=4, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                    first_iteration=first_iteration, k_fold_step=k_fold_step, k_fold_dir=k_fold_dir)
            run_all(part=5, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                    first_iteration=first_iteration, k_fold_step=k_fold_step, k_fold_dir=k_fold_dir)
            run_all(part=6, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                    first_iteration=first_iteration, k_fold_step=k_fold_step, k_fold_dir=k_fold_dir)

            # Copy also the classification maps of the fold
            main_dir = global_parameters["user_choices"]["main_dir"]
            current_kfold_dir_step = op.join(
                main_dir, 'Statistics', 'K_fold_{}'.format(k_fold_step))
            out_files_names = ['labeled_img.tif', 'labeled_img_regular.tif',
                               'contours_superposition.png', 'colorized_classif.png']
            for name in out_files_names:
                src = op.join(main_dir, 'Out', name)
                dst = op.join(current_kfold_dir_step, name)
                shutil.copy(src, dst)

        metrics_exploitation.retrieve_Kfold_data(global_parameters, metrics_plotting=True)
        return

    if user_input == 0:
        run_all(part=1, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                first_iteration=first_iteration, location=location, wanted_date=wanted_date, clear_date=clear_date, force=force)
    elif user_input == 1:
        run_all(part=2, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                first_iteration=first_iteration, force=force)
        run_all(part=3, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                first_iteration=first_iteration, force=force)
        run_all(part=4, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                first_iteration=first_iteration, force=force)
        run_all(part=5, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                first_iteration=first_iteration, force=force)
        run_all(part=6, global_parameters=global_parameters, paths_parameters=paths_parameters, model_parameters=model_parameters,
                first_iteration=first_iteration, force=force)
    else:
        print('Please enter a valid step value [0 or 1]')


if __name__ == '__main__':
    main()

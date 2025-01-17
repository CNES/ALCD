# -*- coding: utf-8 -*-
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (L1C_band_composition.py)

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
import sys

import otbApplication
import importlib.util
import string
import secrets
import find_directory_names
import glob
import json
import shutil
import subprocess
import tempfile
import argparse
import rasterio
import rioxarray


def create_composit_band(bands_full_paths, out_tif, resolution=60, composit_type='ND'):
    ''' Create a composition of multiple bands. Their order is important !!!
    The composition type is defined below
    '''
    tmp_name = next(tempfile._get_candidate_names())
    temp0 = op.join('tmp', 'band1_{}.tif'.format(tmp_name))
    temp1 = op.join('tmp', 'band2_{}.tif'.format(tmp_name))

    resize_band(bands_full_paths[0], out_band=temp0, pixelresX=resolution, pixelresY=resolution)
    resize_band(bands_full_paths[1], out_band=temp1, pixelresX=resolution, pixelresY=resolution)

    temp_bands_full_paths = [str(temp0), str(temp1)]

    # Normalized Difference between band 1 and 2
    if composit_type == 'ND':
        if len(bands_full_paths) != 2:
            print('Impossible to continue: 2 bands needs to be given for the ND')
        else:
            BandMathX = otbApplication.Registry.CreateApplication("BandMathX")
            BandMathX.SetParameterStringList("il", temp_bands_full_paths)
            BandMathX.SetParameterString("out", str(out_tif))
            # 0.01 avoid having NaN in the result
            BandMathX.SetParameterString("exp", "(im1b1-im2b1)/(0.01+im1b1+im2b1)")
            BandMathX.UpdateParameters()
            BandMathX.ExecuteAndWriteOutput()

    # Difference between 1 and 2
    if composit_type == 'D':
        if len(bands_full_paths) != 2:
            print('Impossible to continue: 2 bands needs to be given for the D')
        else:
            BandMathX = otbApplication.Registry.CreateApplication("BandMathX")
            BandMathX.SetParameterStringList("il", temp_bands_full_paths)
            BandMathX.SetParameterString("out", str(out_tif))
            BandMathX.SetParameterString("exp", "(im1b1-im2b1)")
            BandMathX.UpdateParameters()
            BandMathX.ExecuteAndWriteOutput()

    # Ratio between 1 and 2
    if composit_type == 'R':
        if len(bands_full_paths) != 2:
            print('Impossible to continue: 2 bands needs to be given for the R')
        else:
            BandMathX = otbApplication.Registry.CreateApplication("BandMathX")
            BandMathX.SetParameterStringList("il", temp_bands_full_paths)
            BandMathX.SetParameterString("out", str(out_tif))
            BandMathX.SetParameterString("exp", "(im1b1+0.01)/(im2b1+0.01)")
            BandMathX.UpdateParameters()
            BandMathX.ExecuteAndWriteOutput()


def create_specific_indices(in_bands_dir, out_tif, indice_name, resolution=60):
    if indice_name == 'NDVI':
        band1 = glob.glob(op.join(in_bands_dir, '*08.jp2'))[0]
        band2 = glob.glob(op.join(in_bands_dir, '*04.jp2'))[0]
        bands_full_paths = [band1, band2]
        create_composit_band(bands_full_paths, out_tif, resolution=resolution, composit_type='ND')

    elif indice_name == 'NDWI':
        band1 = glob.glob(op.join(in_bands_dir, '*03.jp2'))[0]
        band2 = glob.glob(op.join(in_bands_dir, '*08.jp2'))[0]
        bands_full_paths = [band1, band2]
        create_composit_band(bands_full_paths, out_tif, resolution=resolution, composit_type='ND')

    elif indice_name == 'NDCI':
        band1 = glob.glob(op.join(in_bands_dir, '*08.jp2'))[0]
        band2 = glob.glob(op.join(in_bands_dir, '*04.jp2'))[0]
        bands_full_paths = [band1, band2]
        create_composit_band(bands_full_paths, out_tif, resolution=resolution, composit_type='ND')

    elif indice_name == 'NDSI':
        band1 = glob.glob(op.join(in_bands_dir, '*03.jp2'))[0]
        band2 = glob.glob(op.join(in_bands_dir, '*11.jp2'))[0]
        bands_full_paths = [band1, band2]
        create_composit_band(bands_full_paths, out_tif, resolution=resolution, composit_type='ND')

    else:
        print('Please enter a valid indice name')


def create_time_difference_band(global_parameters, paths_parameters, band_num, out_tif, resolution=60):
    '''
    Create a TIF being the difference between the cloudy date and the clear date
    The band_num is the number of the band of interest
    '''
    location = global_parameters["user_choices"]["location"]
    current_date = global_parameters["user_choices"]["current_date"]
    clear_date = global_parameters["user_choices"]["clear_date"]

    current_dir, current_band_prefix, current_date = find_directory_names.get_L1C_dir(
        location, current_date,paths_parameters, display=False)
    clear_dir, clear_band_prefix, clear_date = find_directory_names.get_L1C_dir(
        location, clear_date,paths_parameters, display=False)

    band_num_str = '{:02d}'.format(band_num)

    # search the two files
    band1 = glob.glob(op.join(current_dir, (current_band_prefix + band_num_str + '.jp2')))[0]
    band2 = glob.glob(op.join(clear_dir, (clear_band_prefix + band_num_str + '.jp2')))[0]
    bands_full_paths = [band1, band2]
    # make the difference
    create_composit_band(bands_full_paths, out_tif, resolution=resolution, composit_type='D')

    return


def create_ratio_bands(global_parameters, in_bands_dir, out_dir_bands, resolution=60):
    '''
    Create TIF being the ratio between different bands, defined in the global_parameters
    '''

    ratios = global_parameters["features"]["ratios"]
    out_names = ['ratio_{}.tif'.format(r) for r in ratios]
    out_paths = [op.join(out_dir_bands, n) for n in out_names]

    for k, ratio in enumerate(ratios):
        # for all the ratios to compute
        band1_string = '{:02d}'.format(int(ratio.split('_')[0]))
        band2_string = '{:02d}'.format(int(ratio.split('_')[1]))

        band1 = glob.glob(op.join(in_bands_dir, '*{}.jp2'.format(band1_string)))[0]
        band2 = glob.glob(op.join(in_bands_dir, '*{}.jp2'.format(band2_string)))[0]
        out_tif = out_paths[k]

        bands_full_paths = [band1, band2]
        create_composit_band(bands_full_paths, out_tif, resolution=resolution, composit_type='R')

    return out_paths


def create_contours_density(in_tif, in_channel, out_tif, radius=3, resolution=60):
    '''
    Create a contours density feature from a band
    '''
    tmp_name = next(tempfile._get_candidate_names())
    temp_tif = op.join('tmp', 'band_for_contours_density_{}.tif'.format(tmp_name))
    resize_band(in_tif, out_band=temp_tif, pixelresX=resolution, pixelresY=resolution)

    # Compute the contours of the image
    EdgeExtraction = otbApplication.Registry.CreateApplication("EdgeExtraction")
    EdgeExtraction.SetParameterString("in", str(temp_tif))
    EdgeExtraction.SetParameterInt("channel", int(in_channel))
    EdgeExtraction.SetParameterString("filter", "gradient")
    EdgeExtraction.UpdateParameters()
    EdgeExtraction.Execute()

    # Mean and others moments of the contours
    LocalStatisticExtraction = otbApplication.Registry.CreateApplication("LocalStatisticExtraction")
    LocalStatisticExtraction.SetParameterInputImage(
        "in", EdgeExtraction.GetParameterOutputImage("out"))
    LocalStatisticExtraction.SetParameterInt("channel", 1)
    LocalStatisticExtraction.SetParameterInt("radius", radius)
    LocalStatisticExtraction.UpdateParameters()
    LocalStatisticExtraction.Execute()

    # Only take the mean (1st channel)
    MeanOnly = otbApplication.Registry.CreateApplication("BandMathX")
    MeanOnly.SetParameterString("out", str(out_tif))
    MeanOnly.AddImageToParameterInputImageList(
        "il", LocalStatisticExtraction.GetParameterOutputImage("out"))
    MeanOnly.SetParameterString("exp", "im1b1")
    MeanOnly.UpdateParameters()
    MeanOnly.ExecuteAndWriteOutput()


def create_variation_coeff(in_tif, in_channel, out_tif, radius=3, resolution=60):
    '''
    Create a texture variation coeff feature
    '''
    tmp_name = next(tempfile._get_candidate_names())
    temp_tif = op.join('tmp', 'band_for_contours_density_{}.tif'.format(tmp_name))
    resize_band(in_tif, out_band=temp_tif, pixelresX=resolution, pixelresY=resolution)

    # Mean and others moments of the contours
    LocalStatisticExtraction = otbApplication.Registry.CreateApplication("LocalStatisticExtraction")
    LocalStatisticExtraction.SetParameterString("in", str(temp_tif))
    LocalStatisticExtraction.SetParameterInt("channel", int(in_channel))
    LocalStatisticExtraction.SetParameterInt("radius", radius)
    LocalStatisticExtraction.UpdateParameters()
    LocalStatisticExtraction.Execute()

    # Variation coeff is the variance over the mean
    MeanOnly = otbApplication.Registry.CreateApplication("BandMathX")
    MeanOnly.SetParameterString("out", str(out_tif))
    MeanOnly.AddImageToParameterInputImageList(
        "il", LocalStatisticExtraction.GetParameterOutputImage("out"))
    MeanOnly.SetParameterString("exp", "sqrt(im1b2)/im1b1")
    MeanOnly.UpdateParameters()
    MeanOnly.ExecuteAndWriteOutput()


def compose_bands_heavy(bands_full_paths, out_tif):
    ''' Create a TIF with all the specified bands
    /!\ can be a heavy file
    '''
    if not op.exists(op.dirname(out_tif)):
        os.makedirs(op.dirname(out_tif))
        print(op.dirname(out_tif) + ' created')

    # write the origin of each band in a .txt file
    # to track where they come from
    file_out = open((out_tif[0:-4] + '_bands.txt'), 'w')
    b = 0  # band number
    bands_text = []
    for band in bands_full_paths:
        bands_text.append(str(band))  # band path
        b += 1  # band number
        file_out.write(('B{} : '.format(b) + band + '\n'))
    file_out.close()

    # Stack all the bands into one TIF
    print('  Creation of the main TIF heavy')
    ConcatenateImages = otbApplication.Registry.CreateApplication("ConcatenateImages")
    ConcatenateImages.SetParameterStringList("il", bands_text)
    ConcatenateImages.SetParameterString("out", str(out_tif))
    ConcatenateImages.UpdateParameters()
    ConcatenateImages.ExecuteAndWriteOutput()
    print('Done')


def dtm_addition(location, out_band, resolution=60):
    '''
    Create the adapted Digital Terrain Model
    From the original one, change its resolution
    '''
    paths_configuration = json.load(open(op.join('parameters_files', 'paths_configuration.json')))
    tile = paths_configuration["tile_location"][location]

    original_DTM_dir = paths_configuration["global_chains_paths"]["DTM_input"]
    resized_DTM_dir = paths_configuration["global_chains_paths"]["DTM_resized"]
    if not op.exists(resized_DTM_dir):
        os.makedirs(resized_DTM_dir)
        print(resized_DTM_dir + ' created')

    original_DTM_path = glob.glob(
        op.join(original_DTM_dir, ('*' + tile + '*'), '*.DBL.DIR', '*_ALT_R2.TIF'))[0]
    resized_DTM_path = op.join(
        resized_DTM_dir, ('{}_{}_DTM_{}m.tif'.format(location, tile, resolution)))

    # do the resizing only if the file has not been computed previously
    if not op.exists(resized_DTM_path):
        pixelresX = resolution
        pixelresY = resolution
        resize_band(original_DTM_path, resized_DTM_path, pixelresX, pixelresY)

    shutil.copy(resized_DTM_path, out_band)


def resize_band(in_band, out_band, pixelresX, pixelresY):
    '''
    Resize a band with the given resolution (in meters)
    '''
    if op.exists(out_band):
        os.remove(out_band)
    build_warp = 'gdalwarp -tr {} {} {} {} '.format(pixelresX, pixelresY, in_band, out_band)
    os.system(build_warp)


def load_module(source, module_name=None):
    """
    reads file source and loads it as a module

    source : user's file to load
    module_name : name of module to register in sys.modules

    Return: loaded module
    """
    if module_name is None:
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        symbol = "".join([secrets.choice(alphabet) for i in range(32)])

        module_name = "gensym_" + symbol

    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module

def user_process(raw_img: str, main_dir: str, module_path : str, fct_name : str, location: str, user_path: str):
    """
    Process an input raster image :
    - Rename the bands knows how to apply its process
    - Apply the user-defined function
    - Save the result and update band description txt file.

    Parameters:
    ----------
    raw_img : str
        Path to the input raster image in GeoTIFF format.

    main_dir : str
        The main directory containing project files.

    fct_path : str
        Path to the Python file containing the user's primitive.
        The function must be named `my_process` and take a `xarray.DataArray` as input and returns a modified xarray.DataArray.

    location : str
        A string representing the location identifier used to locate the band description file.

    user_path : str
        Path where the output raster image will be saved.

    Returns:
    -------
    xarray.DataArray
        The processed raster data as a xarray.DataArray.

    Assumptions:
    - The user's function accepts a xarray.DataArray and returns a modified xarray.DataArray.
    """
    with rioxarray.open_rasterio(raw_img) as raw_arr:

        # Read .txt file with band description
        bands_dict = {}
        band_descr = op.join(main_dir, 'In_data', 'Image', location + "_bands_bands.txt")

        # Extract each band name
        with open(band_descr, 'r') as f:
            for line in f:
                band, path = line.strip().split(" : ")
                band_name = path.split(".tif")[0].split("Intermediate/")[-1]
                if ("_B") in band_name:
                    band_name = band_name.split("_")[-1]
                bands_dict[band] = band_name

        # Rename xarray's bands according to the .txt file
        bands_list = list(bands_dict.values())
        out_arr = raw_arr.assign_coords(band=bands_list)

    # Apply user's function
    user_module = load_module(module_path)

    # Warning : user's function has to be named my_process
    user_function = getattr(user_module, fct_name)
    users_arr = user_function(out_arr)
    new_bands_list = list(users_arr.coords['band'].values)

    n_bands, height, width = users_arr.shape
    print(n_bands)
    # Save user's xarray on disk
    with rasterio.open(user_path, 'w', driver='GTiff', height=height, width=width,
                       count=n_bands, dtype=out_arr.dtype, crs=out_arr.rio.crs,
                       transform=out_arr.rio.transform()) as dst:
        for i in range(n_bands):
            dst.write(users_arr[i], i + 1)

    #Update the band description txt file
    with open(band_descr, 'w') as f:
        for b in range(len(new_bands_list)) :
            print(f"B{b + 1} : {new_bands_list[b]}\n")
            f.write(f"B{b + 1} : {new_bands_list[b]}\n")

    return users_arr

def create_image_compositions(global_parameters, location, paths_parameters, current_date, heavy=False, force=False):
    #
    potential_final_tif = op.join(global_parameters["user_choices"]["main_dir"],
                                  'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    print(global_parameters["user_choices"]["main_dir"])
    if op.exists(potential_final_tif) and force == False:
        print('TIF already present, use -force to erase and replace')
        return

    # get the directory of the bands
    bands_dir, band_prefix, date = find_directory_names.get_L1C_dir(
        location, current_date, paths_parameters, display=True)
    # --------------------------------------------
    # ------ Low resolution TIF with all the bands
    # Preparation
    resolution = 60
    out_dir_bands = op.join(global_parameters["user_choices"]["main_dir"], 'Intermediate')

    additional_bands = []

    # Create new indices if needed
    new_indices = global_parameters["features"]["special_indices"]
    for indice in new_indices:
        out_tif = op.join(out_dir_bands, (indice + '.tif'))
        create_specific_indices(bands_dir, out_tif, indice_name=indice, resolution=resolution)
        additional_bands.append(str(out_tif))

    # Create the ratios
    ratios = create_ratio_bands(global_parameters, bands_dir, out_dir_bands, resolution=60)
    additional_bands.extend(ratios)

    use_DTM = str2bool(global_parameters["features"]["DTM"])
    if use_DTM:
        # Append the DTM model
        out_dtm = op.join(out_dir_bands, ('DTM.tif'))
        # try to append it. If an error occurs, the DTM probably does not exist
        # and we will therefore skip this band
        try:
            dtm_addition(location, out_dtm, resolution=resolution)
            additional_bands.append(str(out_dtm))
        except:
            print('ERROR : THE DTM DOES NOT EXIST !!!')

    create_textures = str2bool(global_parameters["features"]["textures"])
    # Create the texture features
    if create_textures:
        band_used_for_contours = 2
        in_tif = glob.glob(
            op.join(bands_dir, '*{}*{:02}.jp2'.format(band_prefix, band_used_for_contours)))[0]
        in_channel = 1

        out_tif = op.join(out_dir_bands, 'density_contours.tif')
        create_contours_density(in_tif, in_channel, out_tif, radius=3)
        additional_bands.append(str(out_tif))
        out_tif = op.join(out_dir_bands, 'variation_coeff.tif')
        create_variation_coeff(in_tif, in_channel, out_tif, radius=3)
        additional_bands.append(str(out_tif))

    # Create time difference features
    bands_num = [int(band) for band in global_parameters["features"]["time_difference_bands"]]
    out_dir_bands = op.join(global_parameters["user_choices"]["main_dir"], 'Intermediate')
    for band_num in bands_num:
        out_tif = op.join(out_dir_bands, ('time_' + str(band_num) + '.tif'))
        create_time_difference_band(global_parameters, paths_parameters, band_num, out_tif, resolution=resolution)
        additional_bands.append(str(out_tif))

    # --- Create the main TIF with low resolution
    # create intermediate resolution files
    intermediate_bands_dir = op.join(global_parameters["user_choices"]["main_dir"], 'Intermediate')
    pixelresX = resolution
    pixelresY = resolution

    # takes all the cloudy date bands
    bands_num = [int(band) for band in global_parameters["features"]["original_bands"]]

    intermediate_sizes_paths = []
    for band in bands_num:
        in_band = str(op.join(bands_dir, band_prefix) + '{:02d}'.format(band)+'.jp2')
        out_band = op.join(intermediate_bands_dir, op.basename(in_band)[0:-4]+'.tif')

        resize_band(in_band, out_band, pixelresX, pixelresY)
        intermediate_sizes_paths.append(out_band)

    out_all_bands_tif = op.join(global_parameters["user_choices"]["main_dir"],
                                'In_data', 'Image', global_parameters["user_choices"]["raw_img"])
    print(out_all_bands_tif)
    input('iciiii')
    # add all the additional bands after the ones of the cloudy dates
    intermediate_sizes_paths.extend(additional_bands)
    intermediate_sizes_paths = [str(i) for i in intermediate_sizes_paths]

    # create the concatenated TIF
    compose_bands_heavy(intermediate_sizes_paths, str(out_all_bands_tif))

    # --------------------------------------------
    # ---- High resolution TIF with some bands only
    # same working principle but with different resolution

    resolution = 20
    # Create the heavy TIF if requested
    if heavy == True:
        # Create new indices if wanted
        new_indices = ['NDVI', 'NDWI']
        out_dir_bands = op.join(global_parameters["user_choices"]["main_dir"], 'Intermediate')
        additional_bands = []
        for indice in new_indices:
            out_tif = op.join(out_dir_bands, (indice + '.tif'))
            create_specific_indices(bands_dir, out_tif, indice_name=indice, resolution=resolution)
            additional_bands.append(str(out_tif))

        # create intermediate resolution files
        intermediate_bands_dir = op.join(
            global_parameters["user_choices"]["main_dir"], 'Intermediate')
        pixelresX = resolution
        pixelresY = resolution

        # The bands to put into the heavy file
        bands_num = [2, 3, 4, 10]

        intermediate_sizes_paths = []
        for band in bands_num:
            in_band = str(op.join(bands_dir, band_prefix) + '{:02d}'.format(band)+'.jp2')
            out_band = op.join(intermediate_bands_dir, op.basename(in_band)[0:-4]+'.tif')

            resize_band(in_band, out_band, pixelresX, pixelresY)
            intermediate_sizes_paths.append(out_band)

        out_heavy_tif = op.join(global_parameters["user_choices"]["main_dir"], 'In_data',
                                'Image', global_parameters["user_choices"]["raw_img"])[0:-4]+'_H.tif'

        intermediate_sizes_paths.extend(additional_bands)
        intermediate_sizes_paths = [str(i) for i in intermediate_sizes_paths]
        compose_bands_heavy(intermediate_sizes_paths, str(out_heavy_tif))


    if "user_module" in list(global_parameters["user_choices"].keys()) :
        print("ENTERED"*20)
        user_process(raw_img = out_all_bands_tif,
                 main_dir = global_parameters["user_choices"]["main_dir"],
                 module_path = global_parameters["user_choices"]["user_module"],
                 fct_name = global_parameters["user_choices"]["user_function"],
                 location = global_parameters["user_choices"]["location"],
                 user_path = out_all_bands_tif)
    return


def create_no_data_tif(global_parameters, paths_parameters, out_tif, dilation_radius=10):
    '''
    Create the no_data TIF using both the clear and cloudy date.
    Used in the 'layers_creation.create_no_data_shp'
    '''
    location = global_parameters["user_choices"]["location"]
    current_date = global_parameters["user_choices"]["current_date"]
    clear_date = global_parameters["user_choices"]["clear_date"]

    current_dir, current_band_prefix, current_date = find_directory_names.get_L1C_dir(
        location, current_date, paths_parameters, display=False)
    clear_dir, clear_band_prefix, clear_date = find_directory_names.get_L1C_dir(
        location, clear_date, paths_parameters, display=False)

    # Band number, the 1 is 20m resolution, change it if
    # other resolution is wanted
    band_num_str = '{:02d}'.format(1)

    cloudy_band = glob.glob(op.join(current_dir, (current_band_prefix + band_num_str + '.jp2')))[0]
    clear_band = glob.glob(op.join(clear_dir, (clear_band_prefix + band_num_str + '.jp2')))[0]

    # Selection of the no_data pixels
    BandMathX = otbApplication.Registry.CreateApplication("BandMathX")
    BandMathX.SetParameterStringList("il", [str(cloudy_band), str(clear_band)])
    expression = "(im1b1 <= 0 or im2b1 <= 0) ? 1 : 0"
    BandMathX.SetParameterString("exp", expression)
    BandMathX.UpdateParameters()
    BandMathX.Execute()
    # Dilatation of the zones, to have some margin. radius in pixels
    Dilatation = otbApplication.Registry.CreateApplication("BinaryMorphologicalOperation")
    Dilatation.SetParameterInputImage("in", BandMathX.GetParameterOutputImage("out"))
    Dilatation.SetParameterString("out", str(out_tif))
    Dilatation.SetParameterString("filter", "dilate")
    Dilatation.SetParameterString("structype", "ball")
    Dilatation.SetParameterInt("xradius", dilation_radius)
    Dilatation.SetParameterInt("yradius", dilation_radius)
    Dilatation.UpdateParameters()
    Dilatation.ExecuteAndWriteOutput()


def str2bool(v):
    '''
    Converts a string to a boolean
    '''
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def main():
    global_parameters = json.load(open(op.join('parameters_files', 'global_parameters.json')))

    out_tif = 'tmp/tmp_tif.tif'
    create_no_data_tif(global_parameters, out_tif, resolution=60)

    current_date = '20170520'
    location = 'Pretoria'

    create_image_compositions(global_parameters, location, current_date, heavy=False)
    return


if __name__ == '__main__':
    main()

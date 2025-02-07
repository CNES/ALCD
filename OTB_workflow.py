#!/usr/bin/python
"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

The code was written by Louis Baetens during a training period at CESBIO, funded by CNES, under the direction of O.Hagolle

==================== Copyright
Software (OTB_workflow.py)

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
import otbApplication
import csv
import subprocess
import xml.etree.ElementTree as ET
import contour_from_labeled
import confidence_map_exploitation

# -------- 0. DIRECTORIES CREATION---------------------


def create_directories(global_parameters):
    '''
    0. Create the directories for the code to work with
    '''
    print("  Creation of the directories")

    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    main_dir = global_parameters["user_choices"]["main_dir"]

    directories = ['', 'In_data', op.join('In_data', 'Masks'), op.join('In_data', 'Image'),
                   'Statistics', op.join('Statistics', 'correlations'),
                   op.join('Statistics', 'features'), 'Samples', 'Models', 'Out',
                   'Other', 'Intermediate', 'Previous_iterations']
    for sub_dir in directories:
        current_dir = op.join(main_dir, sub_dir)
        if not os.path.exists(current_dir):
            os.makedirs(current_dir)
            print(current_dir + ' created')
    print('Done')


# -------- 1. PREPROCESSING---------------------
# ------------ image statistics
def compute_image_stats(global_parameters, proceed=True):
    '''
    4. Compute the images stats
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    raw_img = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    img_stats = op.join(main_dir, 'Statistics', global_parameters["general"]["img_stats"])

    print("  Compute Images Statistics")
    ComputeImagesStatistics = otbApplication.Registry.CreateApplication("ComputeImagesStatistics")
    ComputeImagesStatistics.SetParameterStringList("il", [str(raw_img)])
    ComputeImagesStatistics.SetParameterString("out.xml", str(img_stats))
    ComputeImagesStatistics.ExecuteAndWriteOutput()

    print('Done')
    return img_stats


# ----------- samples preprocessing
def compute_samples_stats(global_parameters, proceed=True):
    '''
    1. Compute the samples stats
    '''
    print( "  Polygon Classes Statistics")

    main_dir = global_parameters["user_choices"]["main_dir"]
    raw_img = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    class_stats = op.join(main_dir, 'Statistics', global_parameters["general"]["class_stats"])
    training_shp = op.join(main_dir, 'Intermediate',
                           global_parameters["general"]["training_shp_extended"])

    no_data_shp = op.join(main_dir, 'In_data', 'Masks',
                          global_parameters["general"]["no_data_mask"])
    no_data_mask = no_data_shp[0:-4] + '.tif'

    PolygonClassStatistics = otbApplication.Registry.CreateApplication("PolygonClassStatistics")
    PolygonClassStatistics.SetParameterString("in", str(raw_img))
    PolygonClassStatistics.SetParameterString("vec", str(training_shp))
    PolygonClassStatistics.SetParameterString("out", str(class_stats))
    PolygonClassStatistics.SetParameterString("mask", str(no_data_mask))
    PolygonClassStatistics.UpdateParameters()
    PolygonClassStatistics.SetParameterStringList("field", ["class"])
    PolygonClassStatistics.ExecuteAndWriteOutput()
    print('Done')

    return class_stats


def get_bands_qty(img_stats):
    '''
    Parse the XML file returned by compute_image_stats to get the
    correct number of bands used
    This is used by function extract_samples()
    '''
    tree = ET.parse(img_stats)
    root = tree.getroot()

    bands_qty = 0
    for k in range(0, len(root)):
        if root[k].attrib["name"] == "mean":
            bands_qty = len(root[k])
            print('There are {} bands used'.format(bands_qty))

    return bands_qty


def get_samples_nb(class_stats):
    '''
    Parse the XML file returned by compute_samples_stats to get the
    samples number per class
    This is used by function select_samples()
    '''
    tree = ET.parse(class_stats)
    root = tree.getroot()

    nbSamples = []
    for k in range(0, len(root)):
        if root[k].attrib["name"] == "samplesPerClass":
            for c in range(0, len(root[k])):
                nbSamples.append(int(root[k][c].attrib["value"]))

    return nbSamples


def select_samples(global_parameters, strategy="smallest", proceed=True):
    '''
    2. Select the samples
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    raw_img = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    training_samples_location = op.join(
        main_dir, 'Samples', global_parameters["general"]["training_samples_location"])
    class_stats = op.join(main_dir, 'Statistics', global_parameters["general"]["class_stats"])
    training_shp = op.join(main_dir, 'Intermediate',
                           global_parameters["general"]["training_shp_extended"])

    rates = op.join(main_dir, 'Statistics', 'rates.csv')

    no_data_shp = op.join(main_dir, 'In_data', 'Masks',
                          global_parameters["general"]["no_data_mask"])
    no_data_mask = no_data_shp[0:-4] + '.tif'

    print("  Training Samples Selection")
    SampleSelection = otbApplication.Registry.CreateApplication("SampleSelection")
    SampleSelection.SetParameterString("in", str(raw_img))
    SampleSelection.SetParameterString("vec", str(training_shp))
    SampleSelection.SetParameterString("mask", str(no_data_mask))
    SampleSelection.SetParameterString("instats", str(class_stats))
    SampleSelection.SetParameterString("out", str(training_samples_location))
    SampleSelection.SetParameterString("outrates", str(rates))
    SampleSelection.SetParameterString("sampler", "random")  # default is periodic

    if strategy == "smallest":
        SampleSelection.SetParameterString("strategy", "smallest")
    elif strategy == "constant":
        SampleSelection.SetParameterString("strategy", "constant")
        minSamplesNb = min(get_samples_nb(class_stats))
        SampleSelection.SetParameterString("strategy.constant.nb", str(minSamplesNb))
    elif strategy.split('_')[0] == "constant":
        SampleSelection.SetParameterString("strategy", "constant")
        SampleSelection.SetParameterString("strategy.constant.nb", str(strategy.split('_')[1]))

    SampleSelection.UpdateParameters()
    SampleSelection.SetParameterStringList("field", ["class"])
    SampleSelection.Execute()
    print('Done')

    return training_samples_location


def extract_samples(global_parameters, proceed=True):
    '''
    3. Extract the samples
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    raw_img = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    training_samples_extracted = op.join(
        main_dir, 'Samples', global_parameters["general"]["training_samples_extracted"])
    training_samples_location = op.join(
        main_dir, 'Samples', global_parameters["general"]["training_samples_location"])

    print("  Training Samples Extraction")
    SampleExtraction = otbApplication.Registry.CreateApplication("SampleExtraction")
    SampleExtraction.SetParameterString("in", str(raw_img))
    SampleExtraction.SetParameterString("vec", str(training_samples_location))
    SampleExtraction.SetParameterString("outfield", "prefix")
    SampleExtraction.SetParameterString("outfield.prefix.name", "band_")
    SampleExtraction.SetParameterString("out", str(training_samples_extracted))
    SampleExtraction.UpdateParameters()
    SampleExtraction.SetParameterStringList("field", ["class"])
    SampleExtraction.ExecuteAndWriteOutput()
    print('Done')

    return training_samples_extracted

# -------- 2. MODEL TRAINING ---------------------


def train_model(global_parameters, model_parameters, shell=True, proceed=True):
    '''
    5. Train the model
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    method = global_parameters["classification"]["method"]
    training_samples_extracted = op.join(
        main_dir, 'Samples', global_parameters["general"]["training_samples_extracted"])
    img_stats = op.join(main_dir, 'Statistics', global_parameters["general"]["img_stats"])

    model_out = op.join(main_dir, 'Models', ('model.' +
                                             global_parameters["classification"]["method"]))

    features = ''
    features_API = []
    nb_feat = get_bands_qty(img_stats)

    for b in range(nb_feat):
        features += (" band_" + str(b))
        features_API.append("band_" + str(b))
    features = features[1:]
    features_API = [str(f) for f in features_API]

    if proceed == True:
        print("  Train Vector Classifier")
        if shell == True:
            # can be run through the API or through the shell
            command = 'otbcli_TrainVectorClassifier -io.vd {} -cfield {} -io.out {} -classifier {} -feat {}'.format(
                training_samples_extracted, "class", model_out, method, str(features))

            model_options = ''
            for key, value in model_parameters[method].items():
                model_options = model_options + ' -classifier.{}.{} {}'.format(method, key, value)

            command = command + model_options
            subprocess.call(command, shell=True)

        else:
            TrainVectorClassifier = otbApplication.Registry.CreateApplication(
                "TrainVectorClassifier")
            TrainVectorClassifier.SetParameterStringList("io.vd", [str(training_samples_extracted)])
            #~ TrainVectorClassifier.SetParameterString("io.stats", str(img_stats))
            TrainVectorClassifier.SetParameterString("io.out", str(model_out))
            TrainVectorClassifier.UpdateParameters()  # Update here, otherwise features wont be recognized
            TrainVectorClassifier.SetParameterStringList("feat", features_API)
            TrainVectorClassifier.SetParameterString("classifier", str(method))

            for key, value in model_parameters[method].items():
                TrainVectorClassifier.SetParameterString(
                    str("classifier.{}.{}".format(method, key)), str(value))

            TrainVectorClassifier.SetParameterStringList("cfield", ["class"])
            TrainVectorClassifier.UpdateParameters()
            TrainVectorClassifier.ExecuteAndWriteOutput()

        print('Done')
    else:
        print("Training not done this time")

    return model_out


# -------- 3. CLASSIFICATION ---------------------

def image_classification(global_parameters, shell=True, proceed=True, additional_name=''):
    '''
    6. Classification on the image
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    raw_img = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    model = op.join(main_dir, 'Models', ('model.'+global_parameters["classification"]["method"]))

    img_labeled = op.join(main_dir, 'Out', global_parameters["general"]["img_labeled"])
    confidence_map = op.join(main_dir, 'Out', "confidence{}.tif".format(additional_name))

    mask_shp = op.join(main_dir, 'In_data', 'Masks', global_parameters["general"]["no_data_mask"])
    mask_tif = mask_shp[0:-4] + '.tif'

    if proceed == True:
        if shell == True:
            print("  Image Classification (shell)")
            command = 'otbcli_ImageClassifier -in {} -model {} -out {} -confmap {} -mask {}'.format(
                raw_img, model, img_labeled, confidence_map, mask_tif)
            subprocess.call(command, shell=True)

        else:
            print("  Image Classification (API)")
            ImageClassifier = otbApplication.Registry.CreateApplication("ImageClassifier")
            ImageClassifier.SetParameterString("in", str(raw_img))
            ImageClassifier.SetParameterString("model", str(model))
            ImageClassifier.SetParameterString("out", str(img_labeled))
            ImageClassifier.SetParameterString("confmap", str(confidence_map))
            ImageClassifier.SetParameterString("mask", str(mask_tif))
            ImageClassifier.UpdateParameters()
            ImageClassifier.ExecuteAndWriteOutput()

        print('Done')
    else:
        print("Classification not done this time")

    return img_labeled


def confidence_map_viz(global_parameters, additional_name=''):
    '''
    6.5 Enhancement of the classification map
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]

    confidence_map_in = op.join(main_dir, 'Out', "confidence{}.tif".format(additional_name))
    confidence_map_out = op.join(
        main_dir, 'Out', "confidence{}_enhanced.tif".format(additional_name))

    confidence_map_exploitation.confidence_map_change(
        confidence_map_in, confidence_map_out, median_radius=11)

    return
# -------- 3. POST-PROCESSING ---------------------


def fancy_classif_viz(global_parameters, proceed=True):
    '''
    7. Fancy visualisation
    Converts the .tif in a .png using a LUT
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]

    img_labeled = op.join(main_dir, 'Out', global_parameters["general"]["img_labeled_regularized"])
    color_table = op.join('color_tables', global_parameters["color_tables"]["otb"])
    out_image_colorized = op.join(main_dir, 'Out', 'colorized_classif.png')

    ColorMapping = otbApplication.Registry.CreateApplication("ColorMapping")
    ColorMapping.SetParameterString("in", str(img_labeled))
    ColorMapping.SetParameterString("method", "custom")
    ColorMapping.SetParameterString("method.custom.lut", str(color_table))
    ColorMapping.SetParameterString("out", str(out_image_colorized))
    ColorMapping.UpdateParameters()
    ColorMapping.ExecuteAndWriteOutput()

    return out_image_colorized


def compute_mat_conf(global_parameters, show=True, proceed=True):
    '''
    8. Confusion matrix
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]

    conf_matrix = op.join(main_dir, 'Statistics',
                          global_parameters["postprocessing"]["confusion_matrix"])

    img_labeled = op.join(main_dir, 'Out', global_parameters["general"]["img_labeled_regularized"])
    validation_shp = op.join(main_dir, 'Intermediate',
                             global_parameters["general"]["validation_shp_extended"])

    print(' Confusion matrix computing')
    print(conf_matrix)
    ComputeConfusionMatrix = otbApplication.Registry.CreateApplication("ComputeConfusionMatrix")
    ComputeConfusionMatrix.SetParameterString("in", str(img_labeled))
    ComputeConfusionMatrix.SetParameterString("ref", "vector")
    ComputeConfusionMatrix.SetParameterString("ref.vector.in", str(validation_shp))
    ComputeConfusionMatrix.SetParameterString("out", str(conf_matrix))
    ComputeConfusionMatrix.UpdateParameters()
    ComputeConfusionMatrix.SetParameterString("ref.vector.field", "class")
    ComputeConfusionMatrix.ExecuteAndWriteOutput()

    print('Done')

    with open(conf_matrix, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = []
        for row in reader:
            rows.append(row)
        if len(rows) >= 2 and len(rows[0]) >= 2:
            rows = rows[2:4]
            TP = rows[0][0]
            FP = rows[0][1]
            FN = rows[1][0]
            TN = rows[1][1]
            print('Confusion matrix:')
            print('{:10}'.format(TP) + ' | ' + '{:10}'.format(FP) +
                  '\n --------------\n' + '{:10}'.format(FN) + ' | ' + '{:10}'.format(TN))

    return conf_matrix


def classification_regularization(global_parameters, proceed=True, radius=2):
    '''
    9. Regularization of the classification map
    '''

    main_dir = global_parameters["user_choices"]["main_dir"]

    img_labeled = op.join(main_dir, 'Out', global_parameters["general"]["img_labeled"])
    img_regularized = op.join(
        main_dir, 'Out', global_parameters["general"]["img_labeled_regularized"])

    ClassificationMapRegularization = otbApplication.Registry.CreateApplication(
        "ClassificationMapRegularization")

    # The following lines set all the application parameters:
    ClassificationMapRegularization.SetParameterString("io.in", str(img_labeled))
    ClassificationMapRegularization.SetParameterString("io.out", str(img_regularized))
    ClassificationMapRegularization.SetParameterInt("ip.radius", radius)
    ClassificationMapRegularization.EnableParameter("ip.suvbool")
    ClassificationMapRegularization.EnableParameter("ip.onlyisolatedpixels")
    ClassificationMapRegularization.SetParameterInt("ip.nodatalabel", 0)
    ClassificationMapRegularization.SetParameterInt("ip.undecidedlabel", 20)
    ClassificationMapRegularization.UpdateParameters()
    ClassificationMapRegularization.ExecuteAndWriteOutput()


def create_contour_from_labeled(global_parameters, proceed=True):
    '''
    10. Create a contour from labeled image
    '''
    main_dir = global_parameters["user_choices"]["main_dir"]
    raw_img = op.join(main_dir, 'In_data', 'Image', global_parameters["user_choices"]["raw_img"])

    labeled_tif = op.join(main_dir, 'Out', global_parameters["general"]["img_labeled_regularized"])
    contour_tif = op.join(op.dirname(labeled_tif), 'contours_labels.tif')

    # Create the contours
    radius = int(global_parameters["training_parameters"]["dilatation_radius"])
    contour_from_labeled.create_labelisation_contours(
        labeled_tif, contour_tif, dilatation_radius=radius)

    # Create the quicklook png of the superimposition
    contour_superposed_png = op.join(op.dirname(labeled_tif), 'contours_superposition.png')
    contour_from_labeled.rgb_contours_stacking(raw_img, contour_tif, contour_superposed_png)

    return


def main():
    global_parameters = json.load(open(op.join('parameters_files', 'global_parameters.json')))
    train_model(global_parameters, shell=False, proceed=True)

    return


if __name__ == '__main__':
    main()

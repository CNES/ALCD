"""
Tool to generate reference cloud masks for validation of operational cloud masks.
The elaboration is performed using an active learning procedure.

==================== Copyright
Software (conftest.py)

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
import pickle
import shutil
import rasterio
import sqlite3
import subprocess
import pandas as pd
import os.path as op
from pathlib import Path

from conftest import ALCDTestsData
from sklearn.base import BaseEstimator


def check_expected_quicklook_results(
        quicklook_dir: Path
) -> tuple[bool, dict]:
    """Check expected final results."""
    content = [str(elem.name) for elem in Path.iterdir(quicklook_dir)]
    expected_files = ["Toulouse_20240120.jpg", "Toulouse_20240120.jpg.aux.xml",
                      "Toulouse_20240305.jpg", "Toulouse_20240305.jpg.aux.xml"]
    files_exists = {}
    for expected_file in expected_files:
        files_exists[expected_file] = expected_file in content
    return all(list(files_exists.values())), files_exists


def check_expected_alcd_results(
        final_dir: Path
) -> tuple[bool, dict]:
    """Check expected final results."""
    content = [str(elem.name) for elem in Path.iterdir(final_dir)]
    expected_files = ["colorized_classif.png",
                      "colorized_classif.png.aux.xml",
                      "confidence_enhanced.tif",
                      "confidence.tif",
                      "contours_labels.tif",
                      "contours_superposition.png",
                      "labeled_img_regular.tif",
                      "labeled_img.tif",
                      "quicklook.png"]
    files_exists = {}
    for expected_file in expected_files:
        files_exists[expected_file] = expected_file in content
    return all(list(files_exists.values())), files_exists


def check_expected_features_alcd(
        feat_dir: Path
) -> tuple[bool, dict]:
    """Check expected alcd features generation files."""
    content = [str(elem.name) for elem in Path.iterdir(feat_dir)]
    expected_files = ["Toulouse_bands_bands.txt", "Toulouse_bands_H_bands.txt",
                      "Toulouse_bands_H.tif", "Toulouse_bands_ROI.tif", "Toulouse_bands.tif"]
    files_exists = {}
    for expected_file in expected_files:
        files_exists[expected_file] = expected_file in content
    return all(list(files_exists.values())), files_exists


def check_expected_features_content_alcd(
        feat_dir: Path
) -> None:
    """
    Check expected ALCD features content generation files.

    This function verifies that the expected feature files are correctly generated
    in the given directory. It performs the following checks:

    Args:
        feat_dir (Path): Path to the directory containing the feature files.

    Raises:
        AssertionError: If any of the following conditions fail:
            - Number of bands in the band description `.txt` file does not match the TIFF file.
            - Band names in `.txt` file are incorrectly formatted.
            - Number of bands in the SQLite database does not match the TIFF file.
    """
    # Extract the number of bands in the user's data
    band_path = op.join(feat_dir, "In_data", "Image", "Toulouse_bands_bands.txt")
    training_samples_extracted = op.join(feat_dir,  "Samples", "training_samples_extracted_user_prim.sqlite")
    
    tif_path = op.join(feat_dir, "In_data", "Image", "Toulouse_bands.tif")
    with rasterio.open(tif_path) as src:
        exp_nband = src.count

    # Open .txt file, check if the number of lines is equal to the number of bands of the tif image
    # and that they start with B{b}
    with open(band_path, 'r') as f:
        b = 1
        lines = f.readlines()
        assert exp_nband == len(lines)
        for line in f:
            band, path = line.strip().split(" : ")
            assert band == f"B{b}"
            b +=1

    connex = sqlite3.connect(str(training_samples_extracted))
    train_data = pd.read_sql_query("SELECT * FROM output", connex)
    bands_sqlite = list(train_data.columns)[4:]
    assert len(bands_sqlite) == exp_nband



def prepare_test_dir(alcd_paths: ALCDTestsData, output_dir : str, method : str, global_param_file : str = "global_parameters.json") -> tuple[Path, Path]:
    """
    Prepares the test directory by copying reference data and updating configuration files.

    Parameters
    ----------
    alcd_paths : ALCDTestsData
        An object containing the paths for the reference run, configuration files,
        and data directories.
    output_dir : Path
        The directory where the test output will be saved.

    Returns
    -------
    tuple[Path, Path]
        A tuple containing the paths to the modified `global_parameters.json` and
        `paths_configuration.json` files.
    """
    shutil.copytree(alcd_paths.reference_run, output_dir, dirs_exist_ok=True)

    with open(alcd_paths.cfg / "paths_configuration.json", "r",
              encoding="utf-8") as parameters_file:
        paths_parameters = json.load(parameters_file)
    with open(alcd_paths.cfg / global_param_file, "r", encoding="utf-8") as parameters_file:
        global_parameters = json.load(parameters_file)

    paths_parameters["global_chains_paths"]["L1C"] = str(alcd_paths.s2_data)
    paths_parameters["data_paths"]["data_alcd"] = str(alcd_paths.s2_data)
    global_parameters["color_tables"]["otb"] = str(alcd_paths.cfg / "otb_table.txt")
    global_parameters["user_choices"]["main_dir"] = str(output_dir)
    global_parameters["classification"]["method"] = str(method)

    if "user_prim" in global_param_file :
        global_parameters["user_choices"]["user_module"] = str(alcd_paths.data_dir / "users_function.py")

    out_global_parameters = output_dir / global_param_file
    with open(out_global_parameters, "w", encoding="utf-8") as parameters_file:
        parameters_file.write(json.dumps(global_parameters, indent=3, sort_keys=True))
    out_path_parameters = output_dir / "paths_configuration.json"
    with open(out_path_parameters, "w", encoding="utf-8") as parameters_file:
        parameters_file.write(json.dumps(paths_parameters, indent=3, sort_keys=True))

    return out_global_parameters, out_path_parameters


def test_run_alcd(alcd_paths: ALCDTestsData) -> None:
    """
    Tests the execution of the ALCD pipeline by running the main ALCD
    script with specific parameters.

    Parameters
    ----------
    alcd_paths : ALCDTestsData
        An object containing paths related to the project, such as configuration
        and data directories.

    Raises
    ------
    AssertionError
        If the ALCD process fails (i.e., returns a non-zero exit code).
    """
    output_dir = alcd_paths.data_dir / "test_run_alcd" / "Toulouse_31TCJ_20240305"
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, output_dir, "rf_otb")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -f True -s 1 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -force False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')
    alcd_results, details = check_expected_alcd_results(
        alcd_paths.data_dir / "test_run_alcd" / "Toulouse_31TCJ_20240305" / "Out")
    assert alcd_results, f"some output files are missing: {', '.join(file_name for file_name, exists in details.items() if not exists)}"


def test_scikit_alcd(alcd_paths: ALCDTestsData) -> None:
    """
    Tests the execution of the ALCD pipeline by running the main ALCD script with specific parameters.

    Parameters
    ----------
    alcd_paths : ALCDTestsData
        An object containing paths related to the project, such as configuration
        and data directories.

    Raises
    ------
    AssertionError
        If the ALCD process fails (i.e., returns a non-zero exit code).
    """
    output_dir = alcd_paths.data_dir / "test_scikit_alcd" / "Toulouse_31TCJ_20240305"
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, output_dir, "rf_scikit")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -f True -s 1 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -force False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')
    alcd_results, details = check_expected_alcd_results(
        alcd_paths.data_dir / "test_scikit_alcd" / "Toulouse_31TCJ_20240305" / "Out")
    assert alcd_results, f"some output files are missing: {', '.join(file_name for file_name, exists in details.items() if not exists)}"

    model_path = alcd_paths.data_dir / "test_scikit_alcd" / "Toulouse_31TCJ_20240305" / "Models"
    model = pickle.load(open(model_path / "model.rf_scikit", 'rb'))
    assert isinstance(model, BaseEstimator), f"Expected a scikit-learn model, got {type(model)}"


def test_user_prim_alcd(alcd_paths: ALCDTestsData) -> None:
    """
    Tests the execution of the ALCD pipeline by running the main ALCD
    script with specific parameters.

    Parameters
    ----------
    alcd_paths : ALCDTestsData
        An object containing paths related to the project, such as configuration
        and data directories.

    Raises
    ------
    AssertionError
        If the ALCD process fails (i.e., returns a non-zero exit code).
    """
    if op.exists(alcd_paths.data_dir / "s2/Toulouse_31TCJ_20240305"):
        shutil.rmtree(alcd_paths.data_dir / "s2/Toulouse_31TCJ_20240305")

    output_dir = alcd_paths.data_dir / "test_user_prim_alcd" / "Toulouse_31TCJ_20240305"
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, output_dir, "rf_scikit","global_parameters_user_prim.json")

    cmd1 = f"python {alcd_paths.project_dir}/all_run_alcd.py -force True -f True  -s 0 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -force False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"
    proc1 = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = proc1.communicate()
    assert proc1.returncode == 0, out.decode('utf-8')

    shutil.copytree(alcd_paths.s2_data / "Toulouse_31TCJ_20240305" / "In_data" / "Image", output_dir / "In_data" / "Image", dirs_exist_ok=True)

    cmd2 = f"python {alcd_paths.project_dir}/all_run_alcd.py -f True -s 1 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -force False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"
    proc2 = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, _ = proc2.communicate()
    assert proc2.returncode == 0, out.decode('utf-8')

    alcd_results, details = check_expected_alcd_results(
        alcd_paths.data_dir / "test_user_prim_alcd" / "Toulouse_31TCJ_20240305" / "Out")
    assert alcd_results, f"some output files are missing: {', '.join(file_name for file_name, exists in details.items() if not exists)}"

    check_expected_features_content_alcd(alcd_paths.data_dir / "test_user_prim_alcd" / "Toulouse_31TCJ_20240305")


def test_run_alcd_gen_features(alcd_paths: ALCDTestsData) -> None:
    """
    Tests the feature generation stage of the ALCD pipeline by running the appropriate ALCD script.

    Parameters
    ----------
    alcd_paths : ALCDTestsData
        An object containing paths related to the project, such as configuration
        and data directories.

    Raises
    ------
    AssertionError
        If the ALCD process fails (i.e., returns a non-zero exit code).
    """
    output_dir = alcd_paths.data_dir / "test_gen_features" / "Toulouse_31TCJ_20240305"
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, output_dir, "rf_otb")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -force True -f 1 -s 0 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"

    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')
    alcd_results, details = check_expected_features_alcd(
        alcd_paths.data_dir / "test_gen_features" / "Toulouse_31TCJ_20240305" / "In_data" / "Image")
    assert alcd_results, f"some output files are missing: {', '.join(file_name for file_name, exists in details.items() if not exists)}"


def test_quicklook(alcd_paths: ALCDTestsData) -> None:
    """
    Tests the generation of quicklook images using the `quicklook_generator.py` script.

    Parameters
    ----------
    alcd_paths : ALCDTestsData
        An object containing paths related to the project, such as configuration directories.

    Raises
    ------
    AssertionError
        If the quicklook generation process fails (i.e., returns a non-zero exit code).
    """
    output_dir = alcd_paths.data_dir / "test_quicklooks" / "Toulouse_31TCJ_20240305"
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, output_dir, "rf_otb")

    cmd = f"python {alcd_paths.project_dir}/quicklook_generator.py -l Toulouse -paths_parameters {paths_param_file}"

    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')
    quicklook_results, details = check_expected_quicklook_results(Path("tmp") / "Toulouse")
    assert quicklook_results, f"some quicklook files are missing: {', '.join(file_name for file_name, exists in details.items() if not exists)}"

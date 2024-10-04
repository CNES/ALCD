import json
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from tests.conftest import ALCDTestsData

def prepare_test_dir(alcd_paths: ALCDTestsData, output_dir) -> tuple[Path, Path]:
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

    with open(alcd_paths.cfg / "paths_configuration.json", "r", encoding="utf-8") as parameters_file:
        paths_parameters = json.load(parameters_file)
    with open(alcd_paths.cfg / "global_parameters.json", "r", encoding="utf-8") as parameters_file:
        global_parameters = json.load(parameters_file)

    paths_parameters["global_chains_paths"]["L1C"] = str(alcd_paths.s2_data)
    global_parameters["color_tables"]["otb"] = str(alcd_paths.cfg / "otb_table.txt")
    global_parameters["user_choices"]["main_dir"] = str(output_dir)

    out_global_parameters = output_dir / "global_parameters.json"
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
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, alcd_paths.data_dir / "test_run_alcd" / "Toulouse_31TCJ_20240305")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -f True -s 1 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -force False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')


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
    global_param_file, paths_param_file = prepare_test_dir(alcd_paths,
                                                           alcd_paths.data_dir / "test_gen_features" / "Toulouse_31TCJ_20240305")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -force True -f 1 -s 0 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"

    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')

def test_quicklook(alcd_paths:ALCDTestsData)->None:
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
    cmd = f"python {alcd_paths.project_dir}/quicklook_generator.py -l Toulouse -paths_parameters {alcd_paths.cfg}/paths_configuration.json"
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    out, _ = proc.communicate()
    assert proc.returncode == 0, out.decode('utf-8')

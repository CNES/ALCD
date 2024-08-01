import json
import shutil
import subprocess

def prepare_test_dir(alcd_paths, output_dir):
    """
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

def test_run_alcd(alcd_paths):

    global_param_file, paths_param_file = prepare_test_dir(alcd_paths, alcd_paths.data_dir / "test_run_alcd" / "Toulouse_31TCJ_20240305")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -f True -s 1 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -force False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"
    # subprocess.run(cmd.split(), capture_output=True, text=True)
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    # Get output as strings
    out, err = proc.communicate()
    print(out)

def test_run_alcd_gen_features(alcd_paths):

    global_param_file, paths_param_file = prepare_test_dir(alcd_paths,
                                                           alcd_paths.data_dir / "test_gen_features" / "Toulouse_31TCJ_20240305")

    cmd = f"python {alcd_paths.project_dir}/all_run_alcd.py -force True -f 1 -s 0 -l Toulouse -d 20240305 -c 20240120 -dates False -kfold False -global_parameters {global_param_file} -paths_parameters {paths_param_file} -model_parameters {alcd_paths.cfg}/model_parameters.json"

    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    # Get output as strings
    out, err = proc.communicate()
    print(out)

def test_quicklook(alcd_paths):
    cmd = f"python {alcd_paths.project_dir}/quicklook_generator.py -l Toulouse -paths_parameters {alcd_paths.cfg}/paths_configuration.json"
    # subprocess.run(cmd.split(), capture_output=True, text=True)
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )

    # Get output as strings
    out, err = proc.communicate()

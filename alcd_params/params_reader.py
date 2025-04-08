import json
from pathlib import Path

from .global_parameters import ALCDConfig
from .models_parameters import MLConfig
from .paths_parameters import ProjectConfig

from typing import Dict, Any, Union

PathLike = Union[str, Path]


def read_global_parameters(json_file: PathLike) -> Dict[str, Any]:
    """
    Load and parse global configuration parameters from a JSON file.

    Parameters
    ----------
    json_file : str, Path
        Path to the JSON file containing global configuration data.

    Returns
    -------
    Dict[str, Any]
        Parsed configuration data as a dictionary.
    """
    with open(str(json_file), "r") as file:
        data = json.load(file)
    return ALCDConfig(**data).model_dump()


def read_models_parameters(json_file: PathLike) -> Dict[str, Any]:
    """
    Load and parse model configuration parameters from a JSON file.

    Parameters
    ----------
    json_file : str, Path
        Path to the JSON file containing model configuration data.

    Returns
    -------
    Dict[str, Any]
        Parsed model configuration data as a dictionary.
    """
    with open(str(json_file), "r") as file:
        data = json.load(file)
    return MLConfig(**data).model_dump()


def read_paths_parameters(json_file: PathLike) -> Dict[str, Any]:
    """
    Load and parse project path configuration parameters from a JSON file.

    Parameters
    ----------
    json_file : str, Path
        Path to the JSON file containing path configuration data.

    Returns
    -------
    Dict[str, Any]
        Parsed path configuration data as a dictionary.
    """
    with open(str(json_file), "r") as file:
        data = json.load(file)
    return ProjectConfig(**data).model_dump()

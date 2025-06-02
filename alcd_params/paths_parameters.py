from pydantic import BaseModel, DirectoryPath
from typing import Dict, Optional


class GlobalChainsPaths(BaseModel):
    """
    Configuration paths for global data chains.

    Attributes
    ----------
    L1C : FilePath
        Path to Level 1C data.
    maja : FilePath
        Path to MAJA-processed data.
    sen2cor : FilePath
        Path to Sen2Cor-processed data.
    fmask : FilePath
        Path to Fmask4 output directory.
    fmask3 : FilePath
        Path to Fmask3 output directory.
    DTM_input : FilePath
        Path to the original DTM (Digital Terrain Model) directory.
    DTM_resized : FilePath
        Path to the resized DTM directory.
    """
    L1C: DirectoryPath
    maja: Optional[str] = None
    sen2cor: Optional[str] = None
    fmask: Optional[str] = None
    fmask3: Optional[str] = None
    DTM_input: Optional[str] = None
    DTM_resized: Optional[str] = None


class DataPaths(BaseModel):
    """
    Paths related to ALCD and PCC datasets.

    Attributes
    ----------
    data_alcd : FilePath
        Path to the ALCD data directory.
    data_pcc : FilePath
        Path to the PCC data directory.
    """
    data_alcd: DirectoryPath
    data_pcc: Optional[str] = None


class TileLocation(BaseModel):
    """
    Mapping of tile names to location codes.

    Attributes
    ----------
    location : Dict[str, str]
        Dictionary mapping descriptive location names to their tile codes.
    """
    location: Dict[str, str]


class ProjectConfig(BaseModel):
    """
    Main configuration paths for the ALCD project, including data paths and tile mappings.

    Attributes
    ----------
    global_chains_paths : GlobalChainsPaths
        Paths for global data chains.
    data_paths : DataPaths
        Paths for ALCD and PCC data.
    tile_location : TileLocation
        Mapping of descriptive names to tile codes.
    """
    global_chains_paths: GlobalChainsPaths
    data_paths: DataPaths
    tile_location: Dict[str, str]

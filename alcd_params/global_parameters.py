from typing import Dict, List, Optional

from pydantic import BaseModel, FilePath, field_validator, ValidationInfo
from datetime import datetime


class Classification(BaseModel):
    """
    Classification configuration for ALCD.

    Attributes
    ----------
    method : str
        The method of classification to be used, e.g., "rf" for random forest.
    """
    method: str


class Features(BaseModel):
    """
    Configuration for feature extraction in ALCD.

    Attributes
    ----------
    DTM : str
        Indicator for whether a Digital Terrain Model (DTM) is used.
    original_bands : List[int]
        List of original spectral bands to include in the feature extraction.
    ratios : List[str]
        Ratios between bands, typically in the format "bandX_bandY".
    special_indices : List[str]
        List of special indices to calculate, e.g., NDVI, NDWI.
    textures : bool
        Whether or not to include texture analysis in feature extraction.
    time_difference_bands : List[int]
        List of bands for which time-difference calculations will be performed.
    """
    DTM: str
    original_bands: List[int]
    ratios: List[str]
    special_indices: List[str]
    textures: bool
    time_difference_bands: List[int]


class General(BaseModel):
    """
    General configuration related to ALCD's internal operations.

    Attributes
    ----------
    class_stats : str
        File name for storing class statistics.
    img_labeled : str
        File name for the labeled image output.
    img_labeled_regularized : str
        File name for the regularized labeled image output.
    img_stats : str
        File name for image statistics.
    merged_layers : str
        File name for storing merged layer shapefile.
    no_data_mask : str
        File name for no-data mask shapefile.
    training_samples_extracted : str
        File name for the extracted training samples.
    training_samples_location : str
        File name for the location of training samples.
    training_sampling : str
        Sampling strategy for training data, e.g., "smallest".
    training_shp : str
        File name for the training shapefile.
    training_shp_extended : str
        File name for the extended training shapefile.
    validation_shp : str
        File name for the validation shapefile.
    validation_shp_extended : str
        File name for the extended validation shapefile.
    """
    class_stats: str
    img_labeled: str
    img_labeled_regularized: str
    img_stats: str
    merged_layers: str
    no_data_mask: str
    training_samples_extracted: str
    training_samples_location: str
    training_sampling: str
    training_shp: str
    training_shp_extended: str
    validation_shp: str
    validation_shp_extended: str


class LocalPaths(BaseModel):
    """
    Paths related to local storage and server configuration.

    Attributes
    ----------
    copy_folder : str
        Path for the folder where data copies are stored.
    current_server : str
        Current server address for data transfer, e.g., "user@server:/path".
    """
    copy_folder: str
    current_server: str


class Mask(BaseModel):
    """
    Configuration for masks in ALCD.

    Attributes
    ----------
    class_name : int
        Identifier for the class associated with the mask.
    shp : str
        File name for the mask shapefile.
    """
    class_name: int
    shp: str


class PostProcessing(BaseModel):
    """
    Configuration for post-processing steps in ALCD.

    Attributes
    ----------
    binary_confusion_matrix : str
        File name for the binary confusion matrix CSV file.
    confusion_matrix : str
        File name for the overall confusion matrix CSV file.
    model_metrics : str
        File name for model performance metrics CSV file.
    """
    binary_confusion_matrix: str
    confusion_matrix: str
    model_metrics: str


class TrainingParameters(BaseModel):
    """
    Parameters for training models in ALCD.

    Attributes
    ----------
    Kfold : int
        Number of folds for K-fold cross-validation.
    dilatation_radius : int
        Radius for dilating the training samples.
    expansion_distance : int
        Distance for expanding the sample areas.
    regularization_radius : int
        Radius for regularization.
    training_proportion : float
        Proportion of the dataset to be used for training.
    """
    Kfold: int
    dilatation_radius: int
    expansion_distance: int
    regularization_radius: int
    training_proportion: float


class UserChoices(BaseModel):
    """
    User-defined settings for the ALCD process.

    Attributes
    ----------
    user_function: Optional[str]
        Name of the user function to apply to the image before training
    user_module: Optional[str]
        Path to the Python file containing the user's process
    clear_date : str
        Date in YYYYMMDD format for a clear-sky image.
    current_date : str
        Current processing date in YYYYMMDD format.
    location : str
        Name of the location being analyzed.
    main_dir : str
        Main directory for data processing and storage.
    raw_img : str
        File path for the raw input image.
    tile : str
        Tile identifier for the region of interest.
    """
    user_function: Optional[str] = None
    user_module: Optional[str] = None
    clear_date: str
    current_date: str
    location: str
    main_dir: str
    raw_img: str
    tile: str

    @field_validator("clear_date", "current_date")
    def parse_yyyymmdd(cls, value: str, info: ValidationInfo) -> str:
        """
        Validates the date format YYYYMMDD and checks if the date is valid.

        Parameters
        ----------
        value : str
            Date string to validate.
        info : ValidationInfo
            Information about the field being validated.

        Returns
        -------
        str
            Validated date string.

        Raises
        ------
        ValueError
            If the date is not in the correct format or is not a valid date.
        """
        if isinstance(value, str) and len(value) == 8:
            try:
                return str(datetime.strptime(value, "%Y%m%d").date())
            except ValueError:
                raise ValueError("dates must be in YYYYMMDD format and a valid date.")
        else:
            raise ValueError("dates must be in YYYYMMDD format.")


class ALCDConfig(BaseModel):
    """
    Main configuration model for the ALCD project.

    Attributes
    ----------
    classification : Classification
        Configuration for the classification method used.
    color_tables : Dict[str, FilePath]
        Dictionary of paths for color tables, with keys representing table names.
    features : Features
        Feature extraction settings.
    general : General
        General operational configurations.
    masks : Dict[str, Mask]
        Dictionary of mask configurations, with mask names as keys.
    postprocessing : PostProcessing
        Settings for post-processing outputs and metrics.
    training_parameters : TrainingParameters
        Training configuration and parameters.
    user_choices : UserChoices
        User-specified configurations and metadata.
    """
    classification: Classification
    color_tables: Dict[str, FilePath]
    features: Features
    general: General
    masks: Dict[str, Mask]
    postprocessing: PostProcessing
    training_parameters: TrainingParameters
    user_choices: UserChoices
    local_paths: LocalPaths
    json_file: Optional[str] = None

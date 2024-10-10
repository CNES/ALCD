import os
from pathlib import Path

import ipywidgets as widgets
from IPython.display import display

from pathlib import Path

import rasterio
from rasterio.plot import show
from rasterio.enums import Resampling
import numpy as np


def show_raster(input_image_r: str, input_image_g: str, input_image_b: str,
                factor: int = 10) -> None:
    """
    Displays an RGB raster image from three separate files containing red, green, and blue bands.
    The image resolution can be reduced by a specified factor.

    The pixel intensity values are rescaled for better visualization.

    Parameters
    ----------
    input_image_r : str
        Path to the file containing the red band (R) of the raster image.
    input_image_g : str
        Path to the file containing the green band (G) of the raster image.
    input_image_b : str
        Path to the file containing the blue band (B) of the raster image.
    factor : int, optional
        Factor by which to reduce the resolution of the image (default is 10).
        The height and width of the output image will be divided by this factor.

    Example
    -------
    >>> show_raster('red_band.tif', 'green_band.tif', 'blue_band.tif', factor=2)
    """

    with rasterio.open(input_image_r) as src:
        new_height = src.height // factor
        new_width = src.width // factor
        raster_data_r = src.read(out_shape=(src.count, new_height, new_width),
                                 resampling=Resampling.nearest)
    with rasterio.open(input_image_g) as src:
        raster_data_g = src.read(out_shape=(src.count, new_height, new_width),
                                 resampling=Resampling.nearest)
    with rasterio.open(input_image_b) as src:
        raster_data_b = src.read(out_shape=(src.count, new_height, new_width),
                                 resampling=Resampling.nearest)

    raster_data = np.concatenate((raster_data_r, raster_data_g, raster_data_b), axis=0)

    # create new range values for visualization purpose
    flat_array = raster_data.flatten()
    lower_bound = np.quantile(flat_array, 0.1)
    upper_bound = np.quantile(flat_array, 0.9999)
    mask = (raster_data >= lower_bound) & (raster_data <= upper_bound)
    filtered_array = np.where(mask, raster_data, 0)
    min_val = filtered_array.min()
    max_val = filtered_array.max()
    rescaled_array = (filtered_array - min_val) / (max_val - min_val) * 255

    show(rescaled_array.astype(np.uint8), title="Raster Data")

def show_tree(directory:Path) -> None:
    """
    Displays the directory structure of a specified directory in a collapsible output section.

    This function executes the `tree` command to get a visual representation of the directory
    structure, and displays it in a Jupyter Notebook. It also provides a button to toggle
    the visibility of the output.

    Parameters
    ----------
    directory : Path
        The path to the directory for which to display the structure.
        This should be a valid directory path.

    Notes
    -----
    - The output is shown using an `Output` widget, which can handle standard output from
      the command.
    - A button is created to allow the user to toggle the visibility of the directory tree output.

    Example
    -------
    >>> from pathlib import Path
    >>> show_tree(Path('.'))  # Displays the structure of the current directory.
    """

    def get_tree(directory="."):
        return os.popen(f"tree {directory}").read()

    output = widgets.Output()
    with output:
        tree_result = get_tree(directory)
        print(tree_result)

    button = widgets.Button(description="Toggle Directory Tree")
    def on_button_clicked(b):
        if output.layout.display == "none":
            output.layout.display = "block"
        else:
            output.layout.display = "none"

    button.on_click(on_button_clicked)
    display(button)
    output.layout.display = "none"
    display(output)
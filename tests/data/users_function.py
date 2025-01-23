import xarray as xr

def my_process(in_tab : xr.DataArray) -> xr.DataArray :
    """
    Computes the NDSI of the input image
    """
    new_band =  (in_tab.loc['B03'] - in_tab.loc['B11']) / (in_tab.loc['B03'] + in_tab.loc['B11'])

    # band_list = list(in_tab.coords['band'].values)
    # band_list.remove("B01")
    band_list = ['B02', 'B03', 'B04', 'B08', 'NDVI', 'NDWI']

    out_tab = in_tab.sel(band=band_list)
    out_tab = xr.concat(
        [
            out_tab,
            new_band.expand_dims(band=["NDSI"]),
        ], dim='band',
    )
    return out_tab



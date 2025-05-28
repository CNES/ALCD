# ALCD documentation

This is the current user manual for the Active Learning Cloud Detection (ALCD). This code produces classification ref-
erence masks from a Sentinel-2 L1C product, and is particularly designed to detect clouds and
cloud shadows. In order to get the best results as possible, while still minimizing the amount
of manual work to get reference pixels, this method is only applicable to dates in a time series
for which one of the next dates is cloud free. 

For a quick start, you can directly go to the {doc}`tutorial <tutorial>` parts.

```{toctree}
:maxdepth: 2
:caption: Content

How to install ALCD <how_to_install_alcd>
configure ALCD <configure_alcd>
ALCD workflow <workflow>
Tutorials <tutorials>
Tips and advice <tips>
Complementary information <complementary_information>
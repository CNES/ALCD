# The elaboration is performed using an active learning procedure.
#
# ==================== Copyright
# Software (Dockerfile)
#
# Copyright© 2019 Centre National d’Etudes Spatiales
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program.  If not, see
# https://www.gnu.org/licenses/gpl-3.0.fr.html

FROM ubuntu:22.04
ARG OTB_RELEASE=9.0.0

# Install system dependencies
COPY system-dependencies.txt .
RUN apt-get update -y \
 && apt-get upgrade -y \
 && cat system-dependencies.txt | DEBIAN_FRONTEND=noninteractive xargs apt-get install -y --no-install-recommends \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* system-dependencies.txt

# Install pre-compiled OTB binaries
RUN curl https://www.orfeo-toolbox.org/packages/archives/OTB/OTB-$OTB_RELEASE-Linux.tar.gz -o OTB-$OTB_RELEASE-Linux.tar.gz

RUN tar xvf OTB-$OTB_RELEASE-Linux.tar.gz --one-top-level="/app/otb" && rm OTB-$OTB_RELEASE-Linux.tar.gz

# Persistent env
ENV CMAKE_PREFIX_PATH=/app/otb
ENV PYTHONPATH=/app/otb/lib/python3/dist-packages:/app/otb/lib/otb/python
ENV GDAL_DRIVER_PATH=disable
ENV GDAL_DATA=/app/otb/share/gdal
ENV PROJ_LIB=/app/otb/share/proj
ENV PATH=/app/otb/bin:$PATH
ENV LD_LIBRARY_PATH=/app/otb/lib:$LD_LIBRARY_PATH
ENV OTB_APPLICATION_PATH=/app/otb/lib/otb/applications
ENV OTB_INSTALL_DIR=/app/otb
ENV LC_NUMERIC=C

# run post install to apply sed commands on cmake files and to get python
# bindings if needed
RUN sh /app/otb/tools/post_install.sh && sh /app/otb/recompile_bindings.sh

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

RUN ln -s /usr/bin/python3 /usr/bin/python

# Default command when using 'docker run' or 'docker create'
CMD /bin/bash
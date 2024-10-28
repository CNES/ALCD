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

from dataclasses import dataclass

import pytest
from pathlib import Path

@dataclass
class ALCDTestsData():
    project_dir: Path
    def __post_init__(self):
        self.data_dir = self.project_dir / "tests" / "data"
        self.cfg = self.data_dir / "cfg"
        self.reference_run = self.data_dir / "ref_inputs" / "Toulouse_31TCJ_20240305"
        self.s2_data = self.data_dir / "s2"

@pytest.fixture
def alcd_paths(request) -> ALCDTestsData:
    return ALCDTestsData(Path(__file__).parent.parent)
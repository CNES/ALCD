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
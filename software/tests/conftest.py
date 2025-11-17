"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add the software directory to the path so imports work
software_dir = Path(__file__).parent.parent
sys.path.insert(0, str(software_dir))






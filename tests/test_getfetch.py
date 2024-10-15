import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from noid_wrapper.noid_client import NoidClient

@pytest.fixture
def noid_client():
    """Fixture to create a NoidClient instance."""
    return NoidClient(config_path="config.yaml")



import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from noid_wrapper.noid_client import NoidClient

from unittest.mock import patch


@pytest.fixture
def noid_client():
    """Fixture to create a NoidClient instance."""
    return NoidClient(config_path="config.yaml")


@patch("subprocess.run")
def test_mint_single_ark(mock_subprocess, noid_client):
    """Test minting a single ARK."""
    mock_subprocess.return_value.stdout = "id: 77981/gmgs1zcrnw"

    ark = noid_client.mint(1)

    assert ark == "77981/gmgs1zcrnw"
    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", ".", "mint", "1"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_mint_multiple_arks(mock_subprocess, noid_client):
    """Test minting multiple ARKs."""
    mock_subprocess.return_value.stdout = "id: 77981/gmgs1zcrnw"

    ark = noid_client.mint(5)

    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", ".", "mint", "5"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_bind_element(mock_subprocess, noid_client):
    """Test binding an element to an ARK."""
    mock_subprocess.return_value.stdout = "Binding successful"

    ark = "77981/gmgs1zcrnw"
    noid_client.bind(ark, "where", "www.uwm.edu")

    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", ".", "bind", "set", ark, "where", "www.uwm.edu"],
        capture_output=True,
        text=True,
        check=True,
    )

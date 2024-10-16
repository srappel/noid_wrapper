import pytest
import sys
import os
import json
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from noid_wrapper.noid_client import NoidClient
from unittest.mock import patch, mock_open, ANY


@pytest.fixture
def noid_client():
    """Fixture to create a NoidClient instance."""
    return NoidClient(config_path="config.yaml")


@patch("subprocess.run")
def test_mint_single_ark(mock_subprocess, noid_client):
    """Test minting a single ARK."""
    mock_subprocess.return_value.stdout = "id: 77981/gmgs1zcrnw"

    ark = noid_client.mint(1)

    expected_path = noid_client.db_path  # Dynamically get db_path from the client
    mock_subprocess.assert_called_once_with(
        [noid_client.noid_path, "-f", expected_path, "mint", "1"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert ark == "77981/gmgs1zcrnw"


@patch("subprocess.run")
def test_mint_multiple_arks(mock_subprocess, noid_client):
    """Test minting multiple ARKs."""
    mock_subprocess.return_value.stdout = "id: 77981/gmgs1zcrnw"

    ark = noid_client.mint(5)

    expected_path = noid_client.db_path  # Dynamically get db_path from the client
    mock_subprocess.assert_called_once_with(
        [noid_client.noid_path, "-f", expected_path, "mint", "5"],
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

    expected_path = noid_client.db_path  # Dynamically get db_path from the client
    mock_subprocess.assert_called_once_with(
        [noid_client.noid_path, "-f", expected_path, "bind", "set", ark, "where", "www.uwm.edu"],
        capture_output=True,
        text=True,
        check=True,
    )

@patch("subprocess.run")
def test_get_all_elements(mock_subprocess, noid_client):
    """Test getting all elements for an ARK."""
    mock_subprocess.return_value.stdout = "id: 77981/gmgs1zcrnw\nsome_value"
    result = noid_client.get("77981/gmgs1zcrnw")

    assert result == "id: 77981/gmgs1zcrnw\nsome_value"
    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "get", "77981/gmgs1zcrnw"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_fetch_all_elements(mock_subprocess, noid_client):
    """Test fetching all elements for an ARK."""
    mock_subprocess.return_value.stdout = "id: 77981/gmgs1zcrnw\nsome_value"
    result = noid_client.fetch("77981/gmgs1zcrnw")

    assert result == "id: 77981/gmgs1zcrnw\nsome_value"
    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "fetch", "77981/gmgs1zcrnw"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_validate_ark_success(mock_subprocess, noid_client):
    """Test successful ARK validation."""
    mock_subprocess.return_value.stdout = "Validation successful"
    result = noid_client.validate("77981/gmgs1zcrnw")

    assert result is True
    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "validate", "-", "77981/gmgs1zcrnw"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_validate_ark_failure(mock_subprocess, noid_client):
    """Test ARK validation failure."""
    mock_subprocess.return_value.stdout = "iderr: Invalid ID"
    result = noid_client.validate("77981/gmgs1zcrnw")

    assert result is False
    mock_subprocess.assert_called_once_with(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "validate", "-", "77981/gmgs1zcrnw"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("subprocess.run")
def test_bind_multiple_elements(mock_subprocess, noid_client):
    """Test binding multiple elements to an ARK."""
    mock_subprocess.return_value.stdout = "Binding successful"
    ark = "77981/gmgs1zcrnw"
    bind_params = {
        "where": "www.uwm.edu",
        "title": "Test Title",
        "access": "Public"
    }
    result = noid_client.bind_multiple(ark, bind_params)

    assert len(result) == 3
    mock_subprocess.assert_any_call(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "bind", "set", ark, "where", "www.uwm.edu"],
        capture_output=True,
        text=True,
        check=True,
    )
    mock_subprocess.assert_any_call(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "bind", "set", ark, "title", "Test Title"],
        capture_output=True,
        text=True,
        check=True,
    )
    mock_subprocess.assert_any_call(
        ["/usr/local/bin/noid", "-f", noid_client.db_path, "bind", "set", ark, "access", "Public"],
        capture_output=True,
        text=True,
        check=True,
    )


@patch("pathlib.Path.rglob")
def test_process_metadata_files(mock_rglob, noid_client):
    """Test processing metadata files."""
    # Mock a Path object for the file
    mock_path = Path("test_file.json")
    mock_rglob.return_value = [mock_path]
    
    mock_data = {"dct_identifier_sm": ["ark:/77981/gmgs1zcrnw"]}
    
    # Mock the file opening and reading for the specific Path object
    with patch("pathlib.Path.open", mock_open(read_data=json.dumps(mock_data))):
        documents = noid_client.process_metadata_files("some_directory")

    assert len(documents) == 1
    # Adjust the test to handle ark_id being a list
    assert documents[0][0] == ["ark:/77981/gmgs1zcrnw"]

@patch.object(NoidClient, 'bind_multiple')
@patch.object(NoidClient, 'validate', return_value=True)
@patch("pathlib.Path.rglob")
def test_bind_directory_success(mock_rglob, mock_validate, mock_bind_multiple, noid_client, tmp_path):
    """Test binding directory with valid metadata files."""
    # Mock a Path object for the file
    mock_path = tmp_path / "metadata.json"
    mock_rglob.return_value = [mock_path]

    # Create valid metadata for testing
    metadata = {
        "dct_identifier_sm": ["ark:/77981/gmgs1zcrnw"],
        "dct_title_s": "Test Title",
        "dct_accessRights_s": "Public",
        "dct_references_s": json.dumps({
            "http://schema.org/url": "https://geodiscovery.uwm.edu/catalog/ark:/77981/gmgs1zcrnw",
            "http://schema.org/downloadUrl": "https://geodiscovery.uwm.edu/download/ark:/77981/gmgs1zcrnw"
        })
    }

    with mock_path.open("w") as f:
        json.dump(metadata, f)

    param_map = {
        "where": "dct_references_s",
        "title": "dct_title_s",
        "download": "dct_references_s",
        "identifier": "dct_identifier_sm",
        "ogm_aardvark_id": "id",
        "access": "dct_accessRights_s",
    }

    result = noid_client.bind_directory(tmp_path, param_map)

    assert result["success"] == 1
    assert result["failed"] == 0
    assert result["warning"] == 0
    mock_bind_multiple.assert_called_once_with("77981/gmgs1zcrnw", ANY)


@patch.object(NoidClient, 'bind_multiple')
@patch.object(NoidClient, 'validate', return_value=False)
@patch("pathlib.Path.rglob")
def test_bind_directory_invalid_identifier(mock_rglob, mock_validate, mock_bind_multiple, noid_client, tmp_path):
    """Test binding directory with invalid identifiers."""
    # Mock a Path object for the file
    mock_path = tmp_path / "metadata.json"
    mock_rglob.return_value = [mock_path]

    # Create metadata with invalid identifier for testing
    metadata = {
        "dct_identifier_sm": ["invalid_ark"],
        "dct_title_s": "Test Title",
        "dct_accessRights_s": "Public",
        "dct_references_s": json.dumps({
            "http://schema.org/url": "https://geodiscovery.uwm.edu/catalog/invalid_ark",
            "http://schema.org/downloadUrl": "https://geodiscovery.uwm.edu/download/invalid_ark"
        })
    }

    with mock_path.open("w") as f:
        json.dump(metadata, f)

    param_map = {
        "where": "dct_references_s",
        "title": "dct_title_s",
        "download": "dct_references_s",
        "identifier": "dct_identifier_sm",
        "ogm_aardvark_id": "id",
        "access": "dct_accessRights_s",
    }

    result = noid_client.bind_directory(tmp_path, param_map)

    assert result["success"] == 0
    assert result["failed"] == 1
    assert result["warning"] == 0
    mock_bind_multiple.assert_not_called()


@patch.object(NoidClient, 'bind_multiple')
@patch.object(NoidClient, 'validate', return_value=True)
@patch("pathlib.Path.rglob")
def test_bind_directory_with_warnings(mock_rglob, mock_validate, mock_bind_multiple, noid_client, tmp_path):
    """Test binding directory with missing elements (warnings)."""
    # Mock a Path object for the file
    mock_path = tmp_path / "metadata.json"
    mock_rglob.return_value = [mock_path]

    # Create metadata with missing title and accessRights
    metadata = {
        "dct_identifier_sm": ["ark:/77981/gmgs1zcrnw"],
        "dct_references_s": json.dumps({
            "http://schema.org/url": "https://geodiscovery.uwm.edu/catalog/ark:/77981/gmgs1zcrnw",
            "http://schema.org/downloadUrl": "https://geodiscovery.uwm.edu/download/ark:/77981/gmgs1zcrnw"
        })
    }

    with mock_path.open("w") as f:
        json.dump(metadata, f)

    param_map = {
        "where": "dct_references_s",
        "title": "dct_title_s",  # Missing title
        "download": "dct_references_s",
        "identifier": "dct_identifier_sm",
        "ogm_aardvark_id": "id",
        "access": "dct_accessRights_s",  # Missing accessRights
    }

    result = noid_client.bind_directory(tmp_path, param_map)

    assert result["success"] == 1
    assert result["failed"] == 0
    assert result["warning"] == 2  # Title and accessRights missing
    mock_bind_multiple.assert_called_once_with("77981/gmgs1zcrnw", ANY)


@patch.object(NoidClient, 'bind_multiple')
@patch.object(NoidClient, 'validate', return_value=True)
@patch("pathlib.Path.rglob")
def test_bind_directory_with_invalid_json(mock_rglob, mock_validate, mock_bind_multiple, noid_client, tmp_path):
    """Test binding directory with invalid JSON in metadata file."""
    # Mock a Path object for the file
    mock_path = tmp_path / "metadata.json"
    mock_rglob.return_value = [mock_path]

    # Invalid JSON in metadata
    invalid_metadata = '{"dct_identifier_sm": ["ark:/77981/gmgs1zcrnw"], "dct_title_s": "Test Title"'

    mock_path.write_text(invalid_metadata)

    param_map = {
        "where": "dct_references_s",
        "title": "dct_title_s",
        "download": "dct_references_s",
        "identifier": "dct_identifier_sm",
        "ogm_aardvark_id": "id",
        "access": "dct_accessRights_s",
    }

    with pytest.raises(json.JSONDecodeError):
        result = noid_client.bind_directory(tmp_path, param_map)

    mock_bind_multiple.assert_not_called()

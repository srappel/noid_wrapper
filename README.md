
# NOID Wrapper for Python

This Python library provides a wrapper around the [NOID](https://metacpan.org/dist/Noid/view/noid) (Nice Opaque Identifier) Perl utility, making it easier to interact with NOID minting, binding, and retrieving functionality from Python scripts.

## Features

- **Minting Identifiers**: Easily mint a specified number of new identifiers.
- **Binding Metadata**: Bind multiple metadata elements to identifiers.
- **Fetching Metadata**: Retrieve metadata associated with an identifier.
- **Validating ARKs**: Validate identifiers according to NOID rules.
- **Process Metadata Files**: Recursively process metadata files in JSON format to extract and bind identifiers.

## Installation

1. **Fork & Clone the Repository:**

2. **Create and Activate a Virtual Environment:**

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install Dependencies:**

     ```bash
     poetry install
     ```

## Usage

### Configuration

The `config.yaml` file should specify the path to the NOID utility and the database location:

```yaml
NOID:
  noid_path: "/usr/local/bin/noid"
  db_path: "/path/to/noid/database"
  
Logging:
  level: "INFO"
```

### Example: Binding Metadata from JSON Files

To bind metadata from JSON files located in a directory, use the following Python code:

```python
from noid_client import NoidClient

client = NoidClient("config.yaml")

param_map_agsl_aardvark = {
    "where": "dct_references_s",
    "title": "dct_title_s",
    "download": "dct_references_s",
    "identifier": "dct_identifier_sm",
    "ogm_aardvark_id": "id",
    "access": "dct_accessRights_s",
}

result = client.bind_directory("/path/to/metadata", param_map_agsl_aardvark)
print(result)
```

### Testing

To run the test suite, execute:

```bash
pytest
```

This will run the unit tests located in the `tests` folder.

## License

[MIT License](LICENSE)

## Acknowledgments

This project is based on the [NOID](https://metacpan.org/dist/Noid/view/noid)
utility and is designed to provide a simple Python interface for working with NOID identifiers.


# NOID Wrapper for Python

A simple Python wrapper for interacting with the NOID (Nice Opaque Identifier) utility. This project provides methods for minting ARK identifiers and binding metadata to them using the NOID tool.

## Features

- **Minting IDs**: Generate new identifiers using the NOID utility.
- **Binding Metadata**: Bind metadata elements to IDs with the NOID `bind` command.
- **Logging**: Configurable logging to track operations and commands.
- **Configurable**: Customize NOID paths and other settings via a YAML configuration file.

## Requirements

- Python 3.8+
- [NOID Utility](https://metacpan.org/dist/Noid/view/noid)
- PyYAML (for reading configuration)
- Subprocess (for running NOID commands)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/noid_wrapper.git
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required Python dependencies in the pyproject.toml file:

   ```bash
   pip install .
   ```

4. Ensure that the NOID utility is installed and accessible in your system's `PATH`.

## Configuration

The project uses a YAML configuration file (`config.yaml`) to define paths and logging levels. Example `config.yaml`:

```yaml
NOID:
  noid_path: "/usr/local/bin/noid"
  db_path: "/path/to/noid/database"

Logging:
  level: "INFO"
```

Place this file in the root of your project.

## License

[MIT License](LICENSE)

## Acknowledgments

This project is based on the [NOID](https://metacpan.org/dist/Noid/view/noid) utility and is designed to provide a simple Python interface for working with NOID identifiers.

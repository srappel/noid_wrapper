
# NOID Wrapper

`noid-wrapper` is a Python library that provides a wrapper for interacting with the NOID (Nice Opaque Identifier) Perl utility. 
It allows you to create NOID databases, mint and bind ARK identifiers, and perform various NOID operations.

## Features

- Create NOID databases using templates.
- Mint identifiers based on NOID templates.
- Bind elements to identifiers.
- Fetch and get details for specific identifiers.
- Validate identifiers.
- Bind multiple elements to an identifier in batch.

- Process AGSL metadata files to extract and bind ARK identifiers.


## Configuration

The project uses a YAML configuration file, `config.yaml`, to manage paths, templates, and logging levels. Example configuration:

```yaml
NOID:
  noid_path: "/usr/local/bin/noid"
  db_path: "/home/srappel/noid_wrapper"
  template: ["gmgs.reeeeeek", "long", "77981", "University of Wisconsin-Milwaukee Libraries", "gmgs"]

Logging:
  level: "DEBUG"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Usage

### Create a NoidClient Object and a NOID Database.

The `dbcreate()` method is used to create a NOID database if it does not already exist:

```python
client = NoidClient("/path/to/config.yaml")
if not client.dbexist()[0]:  # Check if the database exists
    client.dbcreate()
```

This code is in the `if __name__ == "__main__"` loop, so it will run if you run noid_client.py.

### Minting Identifiers

To mint a new identifier:

```python
client.mint(count=1)
```

The count defaults to 1, so you can even just run `client.mint()` to get a single identifier!

### Binding Elements

To bind an element to an identifier:

```python
client.bind("identifier", "element", "value", "set")
```

There's also a function for binding multiple elements to an identifier at the same time:

```python
bind_params = {
    "element1": "value1",
    "element2": "value2",
    "element3": "value3"
}

client.bind_multiple("identifier", bind_params, how="set")
```

### Fetching Information for an Identifier

To fetch details for a specific identifier:

```python
client.fetch("identifier")
```

There's one for `get` as well, it works the same way.

### Processing Metadata Files

You can recursively process metadata files in a directory and bind ARK identifiers to a NOID database:

```python
client.bind_directory("/path/to/metadata", param_map)
```

## Development

### Running Tests

To run tests, use `pytest'


### Code Style

This project uses `black` for code formatting. 

To format the code, run `black .`

## License

[MIT License](LICENSE).

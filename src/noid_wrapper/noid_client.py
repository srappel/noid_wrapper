import subprocess
import yaml
import logging
from pathlib import Path
import json


class NoidClient:
    def __init__(self, config_path="config.yaml"):
        self.config = self._load_config(config_path)
        self.noid_path = self.config["NOID"].get("noid_path", "noid")
        self.db_path = self.config["NOID"].get("db_path", ".")
        self._setup_logging()

    def _load_config(self, config_path):
        with open(config_path, "r") as file:
            return yaml.safe_load(file)

    def _setup_logging(self):
        log_level = self.config["Logging"].get("level", "INFO")
        logging.basicConfig(level=getattr(logging, log_level))
        self.logger = logging.getLogger(__name__)

    def mint(self, count=1):
        """Mint a specified number of IDs. Default is 1."""
        self.logger.info(f"Minting {count} new ID(s)...")
        result = self._run_noid_command("mint", str(count))

        if result:
            # Strip the 'id: ' part from the result
            id_string = result.split("id: ")[1].strip()
            self.logger.info(f"Minted ID: {id_string}")
            return id_string
        else:
            self.logger.error("Minting failed or returned no ID")
            return None

    def bind(self, id_string, element, value=None, how="set"):
        """
        Bind a value to an existing ID using the specified method (How).

        Args:
            id_string (str): The id_string identifier.
            element (str): The Element name to bind (use ':' or ':-' for stdin).
            value (str, optional): The value to bind to the element (optional for stdin input).
            how (str, optional): The method of binding (e.g., 'new', 'replace', 'set', etc.). Defaults to 'set'.

        Returns:
            str: The result from the NOID command.

        See https://metacpan.org/dist/Noid/view/noid#noid-bind-How-Id-Element-Value
        """
        self.logger.info(
            f"Binding element '{element}' to id_string {id_string} using '{how}' method..."
        )

        if element in [":", ":-"] and value is None:
            # For stdin-based input, we let NOID read from standard input
            return self._run_noid_command("bind", how, id_string, element)
        elif value:
            # Bind normally with element and value
            return self._run_noid_command("bind", how, id_string, element, value)
        else:
            self.logger.error(
                "Element and Value must be provided or use stdin with ':' or ':-'"
            )
            raise ValueError(
                "Invalid bind arguments: must provide Element and Value or use stdin"
            )

    def bind_multiple(self, ark, bind_params, how="set"):
        """
        Bind multiple elements to an ARK by looping through the bind method.

        Args:
            ark (str): The ARK identifier.
            bind_params (dict): A dictionary of Element-Value pairs to bind.
            how (str, optional): The method of binding (e.g., 'set', 'replace', etc.). Defaults to 'set'.

        Returns:
            list: The results from each bind operation.
        """
        self.logger.info(f"Binding multiple elements to ARK {ark}...")
        results = []

        for element, value in bind_params.items():
            self.logger.debug(f"Binding {element} to {ark} with value {value}")
            result = self.bind(ark, element, value, how)
            results.append(result)

        return results

    def get(self, id_string, elements=None):
        """
        Return the bound values for a given id string.
        Optionally get specific elements.

        Args:
            id_string (str): The identifier to fetch information for.
            elements (list, optional): A list of elements to fetch. Fetches all elements if None.

        Returns:
            str: The information for the given ID.

        Use "fetch" for more verbose, human readable data with associated key values.
        """
        self.logger.info(f"Getting info about {id_string}...")

        if elements:
            # If specific elements are provided, append them to the command
            result = self._run_noid_command("get", id_string, *elements)
        else:
            # Fetch all elements if no specific elements are provided
            result = self._run_noid_command("get", id_string)

        if result:
            self.logger.info(f"Got info for ID: {id_string}\n")
            self.logger.info(f"{result}")
            return result
        else:
            self.logger.error("Get command failed")
            return None

    def fetch(self, id_string, elements=None):
        """
        Return the bound values for a given id string. Optionally fetch specific elements.

        Args:
            id_string (str): The identifier to fetch information for.
            elements (list, optional): A list of elements to fetch. Fetches all elements if None.

        Returns:
            str: The fetched information for the given ID.
        """
        self.logger.info(f"Fetching info about {id_string}...")

        if elements:
            # If specific elements are provided, append them to the command
            result = self._run_noid_command("fetch", id_string, *elements)
        else:
            # Fetch all elements if no specific elements are provided
            result = self._run_noid_command("fetch", id_string)

        if result:
            self.logger.info(f"Fetched info for ID: {id_string}\n")
            self.logger.info(f"{result}")
            return result
        else:
            self.logger.error("Fetching failed")
            return None

    def process_metadata_files(self, base_dir) -> list:
        """Recursively processes metadata files in directories to extract ARK IDs."""
        documents = []
        base_path = Path(base_dir)

        for json_file in base_path.rglob("*.json"):
            with json_file.open("r") as file:
                data = json.load(file)
                ark_id = data.get("dct_identifier_sm")
                if ark_id:
                    documents.append((ark_id, data))

        return documents

    def bind_directory(self, dir, param_map):
        bind_params = {}
        documents = self.process_metadata_files(Path(dir))
        assert isinstance(documents, list)

        successful_binds = 0
        failed_binds = 0
        warnings = 0

        for document in documents:

            identifier = document[0][0]
            noid_id = identifier.removeprefix("ark:/")
            assert isinstance(noid_id, str)

            if not self.validate(noid_id):
                self.logger.warning(f"Invalid identifier for {noid_id}.")
                failed_binds += 1
                continue

            try:
                ogm_aardvark_id = document[1].get(
                    param_map["ogm_aardvark_id"], identifier.replace("/", "-")
                )
            except Exception as e:
                self.logger.warning(f"Invalid identifier for {noid_id}.")
                failed_binds += 1
                continue

            bind_params["identifier"] = identifier
            bind_params["ogm_aardvark_id"] = ogm_aardvark_id

            bind_params["title"] = document[1].get(param_map["title"], "Untitled")
            if bind_params["title"] == "Untitled":
                self.logger.warning(f"No title element found for {noid_id}.")
                warnings += 1
            bind_params["access"] = document[1].get(param_map["access"], "None")
            if bind_params["access"] == "None":
                self.logger.warning(f"No access element found for {noid_id}.")
                warnings += 1
            # references
            try:
                references = json.loads(document[1].get("dct_references_s", "{}"))
            except (json.JSONDecodeError, TypeError):
                references = {}
                self.logger.warning(
                    f"Invalid JSON in 'dct_references_s' for {noid_id}."
                )
                failed_binds += 1
                continue

            bind_params["download"] = references.get(
                "http://schema.org/downloadUrl", "Null"
            )
            if bind_params["download"] == "Null":
                self.logger.warning(f"No download url element found for {noid_id}.")
                warnings += 1

            bind_params["where"] = references.get("http://schema.org/url", "Null")
            if bind_params["where"] == "Null":
                self.logger.warning(f"No where url element found for {noid_id}.")
                warnings += 1

            try:
                self.bind_multiple(noid_id, bind_params)
                successful_binds += 1
            except Exception as e:
                self.logger.error(f"Error binding {noid_id}: {str(e)}")
                failed_binds += 1
                continue

        self.logger.info(
            f"Successful binds: {successful_binds}, Failed binds: {failed_binds}, Warnings: {warnings}"
        )
        return {
            "success": successful_binds,
            "failed": failed_binds,
            "warning": warnings,
        }

    def validate(self, id_string):
        """Validate an identifier."""
        self.logger.info(f"Validating ID {id_string}...")
        result = self._run_noid_command("validate", "-", id_string)

        if "iderr" in result:
            self.logger.error(f"Validation failed for {id_string}: {result}")
            return False
        self.logger.info(f"Validation successful for {id_string}")
        return True

    def _run_noid_command(self, *args):
        """Run a NOID command using subprocess."""
        command = [self.noid_path, "-f", self.db_path] + list(args)
        self.logger.debug(f"Running command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"NOID command failed: {e.stderr}")
            raise
        return result.stdout


if __name__ == "__main__":
    client = NoidClient("/home/srappel/noid_wrapper/config.yaml")

    param_map_agsl_aardvark = {
        "where": "dct_references_s",
        "title": "dct_title_s",
        "download": "dct_references_s",
        "identifier": "dct_identifier_sm",
        "ogm_aardvark_id": "id",
        "access": "dct_accessRights_s",
    }

    result = client.bind_directory(
        "/home/srappel/noid_wrapper/metadata", param_map_agsl_aardvark
    )

    print(result)

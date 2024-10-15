import subprocess
import yaml
import logging


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
        

    def validate(self, id_string):
        """Validate an identifier."""
        self.logger.info(f"Validating ID {id_string}...")
        result = self._run_noid_command("validate", "-", id_string)
        
        if "iderr" in result:
            self.logger.error(f"Validation failed for {id_string}: {result}")
            return False
        self.logger.info(f"Validation successful for {id_string}: {result}")
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
    client = NoidClient()
    ark = client.mint()
    print(f"Minted ARK(s): {ark}")

    # bind_param = ("where", "www.uwm.edu")
    # print(bind_param[0])
    # print(bind_param[1])
    # client.bind(ark, bind_param[0], bind_param[1])

    bind_params = {"where": "uwm.edu", "author": "Stephen", "date": "2024-10-15"}

    client.bind_multiple(ark, bind_params)

    print(client.fetch(ark, elements=["where", "author"]))

    print(client.get(ark, ["where"])) # elements= is optional?

    client.validate(ark)

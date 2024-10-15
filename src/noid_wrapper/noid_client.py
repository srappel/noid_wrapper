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
        """Mint a specified number of ARKs. Default is 1."""
        self.logger.info(f"Minting {count} new ARK(s)...")
        result = self._run_noid_command("mint", str(count))

        if result:
            # Strip the 'id: ' part from the result
            ark_id = result.split("id: ")[1].strip()
            self.logger.info(f"Minted ARK: {ark_id}")
            return ark_id
        else:
            self.logger.error("Minting failed or returned no ARK")
            return None

    def bind(self, ark, element, value=None, how='set'):
        """
        Bind a value to an existing ARK using the specified method (How).
        
        Args:
            ark (str): The ARK identifier.
            element (str): The Element name to bind (use ':' or ':-' for stdin).
            value (str, optional): The value to bind to the element (optional for stdin input).
            how (str, optional): The method of binding (e.g., 'new', 'replace', 'set', etc.). Defaults to 'set'.
        
        Returns:
            str: The result from the NOID command.

        See https://metacpan.org/dist/Noid/view/noid#noid-bind-How-Id-Element-Value
        """
        self.logger.info(f"Binding element '{element}' to ARK {ark} using '{how}' method...")

        if element in [':', ':-'] and value is None:
            # For stdin-based input, we let NOID read from standard input
            return self._run_noid_command("bind", how, ark, element)
        elif value:
            # Bind normally with element and value
            return self._run_noid_command("bind", how, ark, element, value)
        else:
            self.logger.error("Element and Value must be provided or use stdin with ':' or ':-'")
            raise ValueError("Invalid bind arguments: must provide Element and Value or use stdin")


    def _run_noid_command(self, *args):
        """Run a NOID command using subprocess."""
        command = [self.noid_path, '-f', self.db_path] + list(args)
        self.logger.debug(f"Running command: {' '.join(command)}")
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            self.logger.error(f"NOID command failed: {e.stderr}")
            raise
        return result.stdout

if __name__ == '__main__':
    client = NoidClient()
    ark = client.mint(1)
    print(f"Minted ARK(s): {ark}")

    bind_param = ("where", "www.uwm.edu")
    print(bind_param[0])
    print(bind_param[1])
    client.bind(ark, bind_param[0], bind_param[1])
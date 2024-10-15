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
        self.logger.info("Minting a new ARK...")
        return self._run_noid_command("mint", str(count))

    def bind(self, ark, value):
        """Bind a value to an existing ARK."""
        self.logger.info(f"Binding value to ARK {ark}...")
        return self._run_noid_command("bind", ark, value)

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
    ark = client.mint(5)
    print(f"Minted ARK(s): {ark}")
import os
import json


class CredentialsManager:

    _instance = None

    CONFIG_DIR = "credentials"
    CONFIG_FILENAME = "credentials.json"
    DEFAULT_CONFIG = {
        "EXAMPLE_API_NAME": "EXAMPLE_API_KEY"
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CredentialsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure initialization happens only once.
        if not hasattr(self, "_initialized"):
            self._initialized = True

            # Compute the overall project root based on the file location.
            # Here we assume that this file is in a subdirectory of the project root.
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

            # Build the full path to the config directory in the project root.
            config_dir_path = os.path.join(project_root, self.CONFIG_DIR)
            os.makedirs(config_dir_path, exist_ok=True)

            # Build the full path to the configuration file.
            self._config_path = os.path.join(config_dir_path, self.CONFIG_FILENAME)
            self._keys = {}
            self._load_config_file()
            self._override_with_env()

    def _load_config_file(self):
        """
        Loads keys from the configuration file in the config directory.
        If the file does not exist, it is created with DEFAULT_CONFIG.
        """
        if not os.path.exists(self._config_path):
            with open(self._config_path, "w") as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            print(f"Created default {self.CONFIG_DIR} file at: {self._config_path}")
            self._keys = DEFAULT_CONFIG.copy()
        else:
            try:
                with open(self._config_path, "r") as f:
                    self._keys = json.load(f)
            except Exception as e:
                raise RuntimeError(
                    f"Error reading configuration file {self._config_path}: {e}"
                )

    def _override_with_env(self):
        """
        For each key in the configuration, check if an environment variable exists (using the uppercase name)
        and override the value.
        """
        for key in self._keys.keys():
            env_value = os.getenv(key.upper())
            if env_value:
                self._keys[key] = env_value

    def get_key(self, key_name):
        """
        Retrieve the API key for the given key name.
        Raises a ValueError if the key is not set or still holds a placeholder.
        """
        key = self._keys.get(key_name)
        if key is None or key.startswith("Your"):
            raise ValueError(
                f"API key for '{key_name}' is not set. Please update {self._config_path} with your actual API key."
            )
        return key

    def set_key(self, key_name, key_value):
        """
        Update or add an API key dynamically, then save the updated configuration.
        """
        self._keys[key_name] = key_value
        self._save_config()

    def _save_config(self):
        """
        Save the current API keys to the configuration file.
        """
        try:
            with open(self._config_path, "w") as f:
                json.dump(self._keys, f, indent=4)
        except Exception as e:
            print(f"Error saving configuration file: {e}")


# Example usage:
if __name__ == "__main__":

    manager = CredentialsManager()

    # Attempt to retrieve good key
    try:
        example_name = list(manager.DEFAULT_CONFIG.keys())[0]
        example_key = manager.get_key(example_name)
        print(f"example_api key loaded for, {example_name}: {example_key}")
    except ValueError as e:
        print(e)

    # Attempt to retrieve bad key
    try:
        example_name = "some_bad_example"
        example_key = manager.get_key(example_name)
        print(f"example_api key loaded for, {example_name}: {example_key}")
    except ValueError as e:
        print(e)

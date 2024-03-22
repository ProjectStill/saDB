import configparser
import os

_CONFIG_PATH = "/etc/sadb.conf"
_USER = os.getlogin()


class ConfigException(Exception):
    def __init__(self, message):
        super().__init__("There was an error parsing /etc/sadb.conf:\n" + message)


# This likely doesn't need to be a class for just one setting
# and a few methods. But this future-proofs it for if we need
# to add more settings later.
class SadbConfig:
    config: configparser.ConfigParser = configparser.ConfigParser()
    # Sets db_location to  string from home folder + .local/share/sadb/sadb.db
    db_location: os.fspath(os.path.join(os.path.expanduser('~'), ".local", "share", "sadb", "sadb.db"))
    repo_url: str

    def __init__(self):  # Loads config file
        self.config.read(_CONFIG_PATH)

        # Load system config first and then any user overrides
        try:
            self.repo_url = self.config["SYSTEM"]["repo_url"]
        except ValueError:
            raise ConfigException("Missing SYSTEM repo_url")

        # Allows overriding db_location in the config file
        if "db_location" in self.config["SYSTEM"]:
            self.db_location = self.config["SYSTEM"]["db_location"]

        # Load any user settings
        if _USER in self.config.sections():
            user_config = self.config[_USER]
            if "repo_url" in user_config:
                self.repo_url = user_config["repo_url"]
            if "db_location" in user_config:
                check_path_valid(user_config["db_location"])
                self.db_location = user_config["db_location"]


def check_path_valid(path: str, section: str) -> bool:
    if not os.path.exists(path):
        raise ConfigException(f"Path {path} for {section} does not exist")
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
class Config:
    config: configparser.ConfigParser = configparser.ConfigParser()
    db_location: os.path.join(os.path.expanduser('~'), ".local", "share", "sadb", "sadb.db")
    repo_url: str

    def __init__(self):  # Loads config file
        self.config.read(_CONFIG_PATH)

        # Load system config first and then any user overrides
        try:
            self.repo_url = self.config["SYSTEM"]["repo_url"]
        except ValueError:
            raise ConfigException("Missing SYSTEM repo_url")

        # Load any user settings
        if _USER in self.config.sections():
            user_config = self.config[_USER]
            if "repo_url" in user_config:
                self.repo_url = user_config["repo_url"]

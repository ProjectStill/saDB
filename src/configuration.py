import configparser
import utilities
import os

# Path to the configuration file
_CONFIG_PATH = "/etc/sadb.conf"

# Current user
_USER = utilities.get_current_user()


class ConfigException(Exception):
    """
    Exception raised for errors in the configuration file.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        super().__init__("There was an error parsing /etc/sadb.conf:\n" + message)


class SadbConfig:
    """
    A class used to represent the configuration of the application.

    ...

    Attributes
    ----------
    config : configparser.ConfigParser
        an instance of ConfigParser
    db_location : str
        the location of the database
    repo_url : str
        the url of the repository
    verbose : bool
        verbosity flag, not set in config file, but used in the program

    Methods
    -------
    __init__(self)
        Initializes the SadbConfig object, loads the configuration file and sets the attributes.
    """

    config: configparser.ConfigParser = configparser.ConfigParser()
    db_location: str = os.fspath(os.path.join("/home", _USER, ".local", "share", "sadb", "sadb.db"))
    repo_url: str
    verbose: bool = False

    def __init__(self):
        """
        Initializes the SadbConfig object, loads the configuration file and sets the attributes.

        Raises
        ------
        ConfigException
            If the configuration file does not exist or if the required keys are not present in the configuration file.
        """

        if not os.path.exists(_CONFIG_PATH):
            raise ConfigException("Config file not found. Please create /etc/sadb.conf with the correct settings.")
        self.config.read(_CONFIG_PATH)

        try:
            self.repo_url = self.config["SYSTEM"]["repo_url"]
        except KeyError:
            raise ConfigException("Missing SYSTEM repo_url")

        if "db_location" in self.config["SYSTEM"]:
            self.db_location = self.config["SYSTEM"]["db_location"]

        if _USER in self.config.sections():
            user_config = self.config[_USER]
            if "repo_url" in user_config:
                self.repo_url = user_config["repo_url"]
            if "db_location" in user_config:
                check_path_valid(user_config["db_location"])
                self.db_location = user_config["db_location"]


def check_path_valid(path: str, section: str) -> bool:
    """
    Checks if the given path exists.

    Parameters
    ----------
    path : str
        The path to check.
    section : str
        The section where the path is defined.

    Raises
    ------
    ConfigException
        If the path does not exist.
    """

    if not os.path.exists(path):
        raise ConfigException(f"Path {path} for {section} does not exist")
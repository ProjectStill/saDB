import io
import os.path
from abc import ABC, abstractmethod
from typing import Optional, List
import configparser

import yaml

class SourceType(ABC):
    """
    Abstract base class for different source types.

    Attributes:
        type (str): The type of the source.
        title (str): The title of the source.
        config_folder (str): The folder where the configuration for the source is stored.
    """
    type: str
    title: str
    config_folder: str

    @abstractmethod
    def __init__(self, yml: str, source_name: str):
        """
        Abstract method for initializing a source type.

        Args:
            yml (str): The YAML configuration for the source.
            source_name (str): The name of the source.
        """
        pass

    @abstractmethod
    def generate_config(self) -> str:
        """
        Abstract method for generating a configuration for a source type.

        Returns:
            str: The generated configuration.
        """
        pass

    @abstractmethod
    def write_config(self):
        """
        Abstract method for writing a configuration for a source type.
        """
        pass

    @abstractmethod
    def check_config(self) -> bool:
        """
        Abstract method for checking a configuration for a source type.

        Returns:
            bool: True if the configuration is valid, False otherwise.
        """
        pass


class FlatpakType(SourceType):
    """
    Class for handling Flatpak source type.

    Attributes:
        type (str): The type of the source.
        config_folder (str): The folder where the configuration for the source is stored.
        repo_url (str): The URL of the repository for the source.
        homepage (Optional[str]): The homepage of the source.
        description (Optional[str]): The description of the source.
        icon_url (Optional[str]): The URL of the icon for the source.
        gpg (Optional[str]): The GPG key for the source.
        alt_urls (Optional[List[str]]): The alternative URLs for the source.
    """
    type = "flatpak"
    config_folder = "/etc/flatpak/remotes.d/"
    repo_url: str
    homepage: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    gpg: Optional[str] = None
    alt_urls: Optional[List[str]] = None

    def __init__(self, yml: str, source_name: str):
        """
        Initialize a Flatpak source type.

        Args:
            yml (str): The YAML configuration for the source.
            source_name (str): The name of the source.
        """
        data = yaml.safe_load(yml)
        data = data[source_name]
        self.title = source_name
        self.repo_url = data["repo_url"]
        self.homepage = data.get("homepage", None)
        self.description = data.get("description", None)
        self.comment = data.get("comment", None)
        self.icon_url = data.get("icon_url", None)
        self.gpg = data.get("gpg", None)
        self.alt_urls = data.get("alt_urls", None)

    def generate_config(self) -> str:
        """
        Generate a configuration for a Flatpak source type.

        Returns:
            str: The generated configuration.
        """
        config = configparser.ConfigParser()
        config["Flatpak Repo"] = {
            "Title": self.title,
            "Url": self.repo_url
        }
        if self.homepage is not None:
            config["Flatpak Repo"]["Homepage"] = self.homepage
        if self.description is not None:
            config["Flatpak Repo"]["Description"] = self.description
        if self.comment is not None:
            config["Flatpak Repo"]["Comment"] = self.icon_url
        if self.icon_url is not None:
            config["Flatpak Repo"]["Icon"] = self.icon_url
        if self.gpg is not None:
            config["Flatpak Repo"]["GPGKey"] = self.gpg

        with io.StringIO() as output:
            config.write(output)
            return output.getvalue()

    def write_config(self):
        """
        Write the configuration for a Flatpak source type to a file.
        """
        with open(self.config_folder + self.title.lower().replace(" ", "_") + ".repo", "w") as file:
            file.write(self.generate_config())

    def check_config(self) -> (bool, str):
        """
        Check the configuration for a Flatpak source type.

        Returns:
            bool: True if the configuration is valid, False otherwise.
            str: The error message if the configuration is not valid.
        """
        config = configparser.ConfigParser()
        path = self.config_folder + self.title.lower().replace(" ", "_") + ".repo"

        try:
            config.read(path)
        except configparser.ParsingError:
            return False, "Error parsing config file for $"  # The $ will be replaced with the source name

        if "Flatpak Repo" not in config.sections():
            return False, "No Flatpak Repo section in $"

        valid_config = configparser.ConfigParser()
        valid_config.read_string(self.generate_config())

        config = config["Flatpak Repo"]
        valid_config = valid_config["Flatpak Repo"]

        if config["Url"] != valid_config["Url"] and not config["Url"] in self.alt_urls:
            return False, "Repo URL does not match for $"
        if config.get("GPGKey", None) is not None:
            if config["GPGKey"] != valid_config["GPGKey"]:
                return False, "GPG Key does not match for $"
        return True, None


class SnapType(SourceType):
    """
    Class for handling Snap source type.

    Attributes:
        type (str): The type of the source.
        title (str): The title of the source.
        config_folder (str): The folder where the configuration for the source is stored.
        homepage (Optional[str]): The homepage of the source.
        description (Optional[str]): The description of the source.
        icon_url (Optional[str]): The URL of the icon for the source.
    """
    type = "snap"
    title = "Snap Store"
    config_folder = ""

    def __init__(self, yml: str, source_name: str):
        """
        Initialize a Snap source type.

        Args:
            yml (str): The YAML configuration for the source.
            source_name (str): The name of the source.
        """
        data = yaml.safe_load(yml)
        data = data[source_name]
        self.title = source_name
        self.homepage = data.get("homepage", None)
        self.description = data.get("description", None)
        self.icon_url = data.get("icon_url", None)

    def generate_config(self) -> str:
        """
        Generate a configuration for a Snap source type.

        Returns:
            str: The generated configuration.
        """
        pass

    def write_config(self):
        """
        Write the configuration for a Snap source type to a file.
        """
        pass

    def check_config(self) -> (bool, str):
        """
        Check the configuration for a Snap source type.

        Returns:
            bool: True if the configuration is valid, False otherwise.
            str: The error message if the configuration is not valid.
        """
        return (True, None)


class SourceError(Exception):
    """
    Exception class for handling source errors.

    Attributes:
        source (str): The source that caused the error.
        message (str): The error message.
    """
    def __init__(self, source: str, message: str):
        self.source = source
        self.message = message
        super().__init__(f"Error with source {source}: {message}")


sources = {
    "flatpak": FlatpakType,
    "snap": SnapType
}
"""
Dictionary mapping source types to their respective classes.

Attributes:
    flatpak (FlatpakType): The class for handling Flatpak source type.
    snap (SnapType): The class for handling Snap source type.
"""


def check_sources(src_yml: str, testing: bool = False) -> (bool, Optional[Exception]):
    """
    Function to check the configurations for all sources.

    Args:
        src_yml (str): The YAML configuration for the sources.
        testing (bool): Whether the function is being used for testing.

    Returns:
        bool: True if all the configurations are valid, False otherwise.
        Optional[Exception]: The exception if any of the configurations is not valid.
    """
    data = yaml.safe_load(src_yml)
    for source_name in data:
        if data[source_name]["source_type"] not in sources:
            return False, SourceError(source_name, f"Unknown source type: {data[source_name]['type']}")
        try:
            source_class = sources[data[source_name]["source_type"]](src_yml, source_name)
            if testing:
                if not os.path.exists(f"sources/{source_name}"):
                    os.makedirs(f"sources/{source_name}", exist_ok=True)
                source_class.config_folder = f"sources/{source_name}/"
            check_conf = source_class.check_config()
            if not check_conf[0]:
                return False, SourceError(source_name, check_conf[1].replace('$', source_name))

        except Exception as e:
            return False, e
    return True, None


def generate_sources(src_yml: str, testing: bool = False):
    """
    Function to generate the configurations for all sources.

    Args:
        src_yml (str): The YAML configuration for the sources.
        testing (bool): Whether the function is being used for testing.
    """
    data = yaml.safe_load(src_yml)
    for source_name in data:
        try:
            source_class = sources[data[source_name]["source_type"]](src_yml, source_name)
        except KeyError:
            raise SourceError(source_name, f"Unknown source type: {data[source_name]['source_type']}")
        if testing:
            if not os.path.exists(f"sources/{source_name}"):
                os.makedirs(f"sources/{source_name}", exist_ok=True)
            source_class.config_folder = f"sources/{source_name}/"
        check_conf = source_class.check_config()
        if not check_conf[0]:
            source_class.write_config()

    check_conf = check_sources(src_yml)
    if not check_conf[0]:
        raise check_conf[1]
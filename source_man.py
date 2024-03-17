import io
from abc import ABC, abstractmethod
from typing import Optional, List
import configparser

import yaml


class SourceType(ABC):
    type: str
    title: str
    config_folder: str

    @abstractmethod
    def __init__(self, yml: str, source_name: str):
        pass

    @abstractmethod
    def generate_config(self) -> str:
        pass

    @abstractmethod
    def write_config(self):
        pass

    @abstractmethod
    def check_config(self, path: str) -> bool:
        pass


class FlatpakType(SourceType):
    type = "flatpak"
    config_folder = "/etc/flatpak/remotes.d/"
    repo_url: str
    homepage: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    gpg: Optional[str] = None
    alt_urls: Optional[List[str]] = None

    def __init__(self, yml: str, source_name: str):
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

        # Configparser can't write to a string, so we have to use StringIO
        with io.StringIO() as output:
            config.write(output)
            return output.getvalue()

    def write_config(self):
        # write the config file to a real file
        with open(f"/etc/flatpak/remotes.d/{self.title.lower().replace(" ", "_")}", "w") as file:
            file.write(self.generate_config())

    def check_config(self, path: str) -> (bool, str):
        config = configparser.ConfigParser()

        try:
            config.read(path)
        except configparser.ParsingError:
            return False, "Error parsing config file for $"  # The $ will be replaced with the source name

        if "Flatpak Repo" not in config.sections():
            return False, "No Flatpak Repo section in $"

        valid_config = self.generate_config()

        # Focus on the Flatpak Repo section
        config = config["Flatpak Repo"]
        valid_config = valid_config["Flatpak Repo"]

        # Check important values for repo to at least work properly
        if config["Url"] != valid_config["Url"] and not config["Url"] in self.alt_urls:
            return False, "Repo URL does not match for $"
        if config.get("GPGKey", None) is not None:
            if config["GPGKey"] != valid_config["GPGKey"]:
                return False, "GPG Key does not match for $"
        return True, None


class SourceError(Exception):
    """Raised when a source is not properly configured"""
    def __init__(self, source: str, message: str):
        self.source = source
        self.message = message
        super().__init__(f"Error with source {source}: {message}")


sources = {
    "flatpak": FlatpakType
}


def check_sources(src_yml: str) -> (bool, str, str):
    data = yaml.safe_load(src_yml)
    for source_name in data:
        if data[source_name]["type"] not in sources:
            return False, source_name, f"Unknown source type: {data[source_name]['type']}"
        try:
            source_class = sources[data[source_name]["type"]](src_yml, source_name)
            check_conf = source_class.check_config(f"sources/{source_name}.conf")
            if not check_conf[0]:
                return False, source_name, f"Error initializing source: \n{check_conf[1].replace('$', source_name)}"
        except Exception as e:
            return False, source_name, f"Error initializing source: \n{str(e)}"
    return True, None, None


def generate_sources(src_yml: str): # Reads yaml file, finds source type, checks config, and writes config file
    data = yaml.safe_load(src_yml)
    for source_name in data:
        source_class = sources[data[source_name]["type"]](src_yml, source_name)
        check_conf = source_class.check_config(f"sources/{source_name}.conf")  # Will gen config if error
        if not check_conf[0]:
            source_class.write_config()

    check_conf = check_sources(src_yml)

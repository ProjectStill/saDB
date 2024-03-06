from abc import ABC, abstractmethod
from typing import Optional, List
import configparser

import yaml


class SourceType(ABC):
    type: str
    title: str

    @abstractmethod
    def __init__(self, yml: str, source_name: str):
        pass

    @abstractmethod
    def generate_config(self):
        pass

    def write_config(self, path: str):
        # write the config file to a real file
        with open(path, "w") as file:
            self.generate_config().write(file)

    @abstractmethod
    def check_config(self, path: str) -> bool:
        pass


class FlatpakType(SourceType):
    type = "flatpak"
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

    def generate_config(self) -> configparser.ConfigParser:
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
        return config

    def check_config(self, path: str) -> bool:
        config = configparser.ConfigParser()

        try:
            config.read(path)
        except configparser.ParsingError:
            return False

        if "Flatpak Repo" not in config.sections():
            return False

        valid_config = self.generate_config()

        # Focus on the Flatpak Repo section
        config = config["Flatpak Repo"]
        valid_config = valid_config["Flatpak Repo"]

        # Check important values for repo to at least work properly
        if config["Url"] != valid_config["Url"] and not config["Url"] in self.alt_urls:
            return False
        if config.get("GPGKey", None) is not None:
            if config["GPGKey"] != valid_config["GPGKey"]:
                return False
        return True

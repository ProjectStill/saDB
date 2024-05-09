import gzip
import io
from typing import Optional, List
import configparser
import yaml

from sadb import InstalledApp, App
from sadb.database import WritableDB, ReadableDB
from sadb.source import SourceType
from xml.etree import ElementTree as etree

import gi

gi.require_version("Flatpak", "1.0")
gi.require_version("AppStream", "1.0")
from gi.repository import Flatpak, AppStream, GLib

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

    @staticmethod
    def add_installed_to_db(db: WritableDB):
        """
        Method to add installed apps to database
        Args:
            db (WritableDB): database to add apps to
        """
        db.add_installed_apps(FlatpakType.get_installed(db))

        # Check for app in sadb (return it)
        # check if remote is a sadb source
        # Get app from app stream

    @staticmethod
    def get_installed(db: ReadableDB) -> List[InstalledApp]:
        apps = []
        flatpak_installation = Flatpak.Installation.new_system()
        refs = flatpak_installation.list_installed_refs()

        for ref in refs:
            origin = ref.get_origin()
            package = ref.format_ref()

            if package.split("/")[0] != "app":
                continue

            app = db.get_installed_app_from_main_db(origin, package)
            if app is None:
                try:
                    appstream_gz = ref.load_appdata(None).get_data()
                    metadata = AppStream.Metadata()
                    metadata.set_locale("en")
                    metadata.parse_bytes(GLib.Bytes(get_component(gzip.decompress(appstream_gz))), AppStream.FormatKind.XML)
                    app_component = metadata.get_component()
                except GLib.GError:
                    app_component = None

                if app_component is None:
                    app = InstalledApp(
                        False, f"{origin}-{package.split("/")[1].replace(".", "-")}",
                        ref.get_name(), origin, package, "", "Unknown Author", ref.get_name(),
                        "This is an unknown app", ["Unknown"], None, None, None,
                        None, None, None, None, None, None, None,
                        None, None
                    )
                    continue

                icon = app_component.get_icon_by_size(64, 64)
                if icon:
                    icon = icon.get_filename()  # Should be local since app is already installed
                mimetypes = app_component.get_provided_for_kind(AppStream.ProvidedKind.MEDIATYPE)

                if mimetypes is None:
                    mimetypes = []
                else:
                    mimetypes = mimetypes.get_items()

                app = InstalledApp(
                    False, f"{origin}-{package.split("/")[1].replace(".", "-")}",
                    app_component.get_name(), origin, package, icon, app_component.get_developer().get_name(),
                    app_component.get_summary(), app_component.get_description(), app_component.get_categories(),
                    app_component.get_keywords(), mimetypes, None, None, None, None,
                    None, None, None, None, None, None
                )

            app.update_available = not ref.get_is_current()
            apps.append(app)
        return apps


def get_component(input_xml: bytes, language: str = "en") -> Optional[bytes]:
    components = etree.fromstring(input_xml)
    component = components.find("component")

    lang_tag = "{http://www.w3.org/XML/1998/namespace}lang"

    if component is not None:
        for element in list(component):
            if lang_tag in element.attrib and element.attrib[lang_tag] != language:
                component.remove(element)
        return etree.tostring(component, encoding='utf-8')
    return None
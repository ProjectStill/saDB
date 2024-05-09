from typing import Optional, List
import yaml

from sadb.source import SourceType

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

    @staticmethod
    def add_installed_to_db(db):
        pass
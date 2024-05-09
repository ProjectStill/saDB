from abc import ABC, abstractmethod
from sadb.database import WritableDB

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

    @staticmethod
    @abstractmethod
    def add_installed_to_db(db: WritableDB):
        """
        Method to add installed apps to database
        Args:
            db (WritableDB): database to add apps to
        """


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
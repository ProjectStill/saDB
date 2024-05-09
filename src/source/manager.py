import os.path
from typing import Optional

import yaml
from sadb.source import SourceError
from sadb.source.flatpak import FlatpakType
from sadb.source.snap import SnapType


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
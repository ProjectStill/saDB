import requests
from tqdm import tqdm
import os
import pwd


def get_current_user():
    """
    Function to get the current user.

    Returns:
        str: The current user.
    """
    if 'SUDO_USER' in os.environ:
        return os.environ['SUDO_USER']
    else:
        return os.getlogin()


def is_sudo_root():
    """
    Function to check if the current user is a sudo root.

    Returns:
        bool: True if the current user is a sudo root, False otherwise.
    """
    return "SUDO_USER" in os.environ


def fix_perms(path):
    """
    Function to fix the permissions of a file.

    Args:
        path (str): The path of the file.
    """
    uid = pwd.getpwnam(get_current_user()).pw_uid
    os.chown(path, uid, -1)


class DownloadException(Exception):
    """
    Exception class for handling download errors.

    Attributes:
        message (str): The error message.
    """
    def __init__(self, message: str = ""):
        super().__init__("Unable to download yaml file, please check your internet:\n" + message)


def download_yaml(url, verbose=False):
    """
    Function to download a YAML file.

    Args:
        url (str): The URL of the YAML file.
        verbose (bool): Whether to show the progress of the download.

    Returns:
        str: The content of the YAML file.

    Raises:
        DownloadException: If the download fails.
    """
    response = requests.get(url, stream=True)

    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 kb

    response.raise_for_status()

    if verbose:
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    else:
        progress_bar = None

    yaml_data = b''

    for data in response.iter_content(block_size):
        if verbose:
            progress_bar.update(len(data))
        yaml_data += data

    if verbose:
        progress_bar.close()

    if total_size_in_bytes == 0:
        raise DownloadException()

    return yaml_data.decode('utf-8')
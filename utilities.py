import requests
from tqdm import tqdm


def download_yaml(url, verbose=False):
    response = requests.get(url, stream=True)

    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte

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

    if total_size_in_bytes != 0 and (verbose and progress_bar.n != total_size_in_bytes):
        print("ERROR, something went wrong")

    return yaml_data.decode('utf-8')
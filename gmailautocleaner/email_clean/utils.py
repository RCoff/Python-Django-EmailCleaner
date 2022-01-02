import logging
import pickle
from pathlib import Path
import re

logger = logging.getLogger(__name__)


def load_pickle(path: str or Path, on_error: str = 'ignore'):
    logger.debug(f"Loading pickle file at path '{path}'", extra={'path': path})
    path = _parse_file_path(path)

    pickle_data = None
    if Path(path).exists():
        with open(path, 'rb') as pf:
            pickle_data = pickle.load(pf)
    else:
        if on_error.upper() == 'RAISE':
            raise ValueError(f"Path '{path}' not found")
        else:
            logger.debug(f"Path does not exist", extra={'path': path})

    return pickle_data


def save_pickle(data, path: str or Path, protocol=pickle.HIGHEST_PROTOCOL, **kwargs):
    logger.debug(f"Saving pickle file at path {path}", extra={'path': path})
    path = _parse_file_path(path)

    with open(path, 'wb') as pf:
        pickle.dump(data, pf, protocol=protocol, **kwargs)

    logger.debug(f"Pickling complete", extra={'path': path})


def _parse_file_path(path: str or Path):
    if isinstance(path, Path):
        path = Path(path)

    return path


def parse_email_domain(sender_email: str) -> str:
    """

    :param sender_email:
    :return:
    """

    regex_string = r"(?<=@).*\.[a-zA-Z]{2,}(?=\>|$)"
    parsed_sender = re.search(regex_string, sender_email).group(0)

    return parsed_sender

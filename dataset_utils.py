import re
import logging
from pathlib import Path
from functools import reduce

def setup_logger():
    logger = logging.getLogger("DatasetLogger")
    logger.setLevel(logging.DEBUG)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch_formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(ch_formatter)

    # File Handler
    fh = logging.FileHandler("logs/dataset.log")
    fh.setLevel(logging.DEBUG)
    fh_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(fh_formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger

def fix_scientific_notation(value: str) -> float:
    """Convert incorrectly formatted scientific notation to proper float."""
    # Match numbers with incorrect scientific notation (e.g., "-2.959-3" → "-2.959e-3")
    corrected_value = re.sub(r'(?<=\d)-(\d+)$', r'e-\1', value)
    return float(corrected_value)


def get_files_from_var_dirs(base_dir, variant):
	"""
	Traverse through all Var_<no> directories and get files matching the pattern.	
	:param base_dir: The base directory containing Var_<no> directories.
	:param pattern: The file pattern to match (e.g., "*.fem").
	:return: A dictionary where keys are Var_<no> paths and values are lists of matching files.
	"""
	var_files = []
	patterns = ["FYP*.nas", "*.pch", "CBUSH*.nas", "*.fem"]
	# Iterate over all Var_<no> directories
	for var_dir in Path(base_dir).glob(variant):
		# Find files matching the pattern in the current Var_<no>/_files_ directory
		matching_files = [list(var_dir.rglob(patterns[i]))[0] for i in range(len(patterns))]
		var_files = [str(file) for file in matching_files]	
	return var_files


def get_nested_value(data, keys, default=None):
    """
    Retrieve a value from a nested dictionary using a list of keys.

    :param data: The dictionary to search.
    :param keys: A list of keys representing the path to the desired value.
    :param default: The default value to return if the path doesn't exist.
    :return: The value at the specified path or the default value.
    """
    try:
        return reduce(lambda d, key: d[key], keys, data)
    except (KeyError, TypeError):
        return default

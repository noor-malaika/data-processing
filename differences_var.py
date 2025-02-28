import os
import glob
import subprocess as sp
from itertools import combinations
import logging
def find_missing_numbers(sorted_sequence):
    """
    Finds missing numbers in a sorted sequence of integers.
    
    :param sorted_sequence: List[int] - A sorted list of integers
    :return: List[int] - A list of missing integers
    """
    missing_numbers = []
    if not sorted_sequence:
        return missing_numbers

    for i in range(len(sorted_sequence) - 1):
        current = sorted_sequence[i]
        next_num = sorted_sequence[i + 1]
        # Check for gaps between consecutive numbers
        if next_num - current > 1:
            missing_numbers.extend(range(current + 1, next_num))

    return missing_numbers

data_dir = "results_v1_split/"
paths = os.listdir(data_dir)
paths = [int(path.split('_')[-1]) for path in paths]
paths = sorted(paths)
print(find_missing_numbers(paths))

data_dir = "/home/sces55/Malaika/fyp/data_processing/results_v1_split/**/FYP*.nas"
# data_dir = "/home/sces55/Malaika/fyp/data_processing/results_v1_split/**/*.pch"


logging.basicConfig(
    level=logging.DEBUG,  # Set the level to DEBUG to capture all logs
    format="%(asctime)s - %(levelname)s - %(message)s",  # Customize the log format
    handlers=[
        logging.FileHandler("test_returncode.log")  # Save logs to a file
    ]
)

cmd_arr = []
paths = glob.glob(data_dir, recursive=True)
combs_to_compare = list(combinations(paths,2))

for p in combs_to_compare[1000:1005]:
    cmd_arr = ["diff",*p]
    result = sp.run(cmd_arr, capture_output=True)
    logging.info(f"Ouput for {' '.join(cmd_arr)}: {result}")

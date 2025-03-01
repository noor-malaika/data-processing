import os
import h5py
from dataset_utils import get_files_from_var_dirs, setup_logger
from data_to_hdf5 import Dataset


def main():

    logger = setup_logger()
    base_dir = "results_v1_split"
    data_file = h5py.File("hdf5_data/dataset.hdf5", "w")
    variants = next(os.walk(base_dir))[1]

    if not variants:
        logger.error("No variants found in the base directory.")
        return 1

    for variant in variants:
        logger.info(f"Processing variant: {variant}")
        try:
            geom, pch, constr, fem = get_files_from_var_dirs(base_dir, variant, logger)
            reader = Dataset(logger)
            reader.read(geom, constr, fem, pch)
            reader.create_hdf5(data_file, variant)
        except Exception as e:
            logger.error(f"Error occured adding {variant} to Dataset - {e}")
            continue

    data_file.close()
    logger.info("HDF5 file closed successfully.")

    return 0


if __name__ == "__main__":
    main()

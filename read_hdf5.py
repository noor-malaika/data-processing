import h5py


def read_hdf5_structure(file_path):
    """Recursively reads and prints the structure of an HDF5 file.

    Args:
        file_path (str): Path to the HDF5 file.
    """

    def print_structure(name, obj):
        """Helper function to print dataset names and shapes."""
        if isinstance(obj, h5py.Group):
            print(f"📂 Group: {name}")
        elif isinstance(obj, h5py.Dataset):
            print(f"📄 Dataset: {name} | Shape: {obj.shape} | Type: {obj.dtype}")

    # Open the HDF5 file and iterate over items
    with h5py.File(file_path, "r") as hdf_file:
        hdf_file.visititems(print_structure)


# Example usage
file_path = "hdf5_data/dataset.hdf5"  # Replace with your actual HDF5 file path
# read_hdf5_structure(file_path)

with h5py.File(file_path, "r") as f:
    # Count the number of top-level groups
    num_top_level_groups = sum(1 for item in f.values() if isinstance(item, h5py.Group))

    print(f"Number of top-level groups: {num_top_level_groups}")

with h5py.File(file_path, "r") as f:
    # Initialize a counter for level 2 groups
    num_level2_groups = 0

    # Iterate over top-level groups
    for top_level_group in f.values():
        if isinstance(top_level_group, h5py.Group):
            # Count subgroups (level 2 groups) within the top-level group
            num_level2_groups += sum(
                1 for item in top_level_group.values() if isinstance(item, h5py.Group)
            )

    print(f"Number of level 2 groups: {num_level2_groups}")

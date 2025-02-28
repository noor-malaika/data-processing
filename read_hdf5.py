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
    with h5py.File(file_path, 'r') as hdf_file:
        hdf_file.visititems(print_structure)

# Example usage
file_path = "hdf5_data/dataset.hdf5"  # Replace with your actual HDF5 file path
read_hdf5_structure(file_path)

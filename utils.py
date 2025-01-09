import vtk
import h5py
import numpy as np


def loadmat(filename):
    """
    Load MATLAB v7.3 format .mat file using h5py.

    Args:
        filename (str): Path to the .mat file.

    Returns:
        dict: Dictionary of data loaded from the .mat file.
    """
    with h5py.File(filename, 'r') as f:
        data = {}
        for k, v in f.items():
            if isinstance(v, h5py.Dataset):
                data[k] = v[()]
            elif isinstance(v, h5py.Group):
                data[k] = loadmat_group(v)
    return data


def loadmat_group(group):
    """
    Load a group from MATLAB v7.3 format .mat file using h5py.

    Args:
        group (h5py.Group): Group from an HDF5 file.

    Returns:
        dict: Dictionary of data within the group.
    """
    data = {}
    for k, v in group.items():
        if isinstance(v, h5py.Dataset):
            data[k] = v[()]
        elif isinstance(v, h5py.Group):
            data[k] = loadmat_group(v)
    return data


def load_kdata(filename):
    """
    Load k-space data from a .mat file.

    Args:
        filename (str): Path to the .mat file.

    Returns:
        np.ndarray: K-space data with shape [nt, nz, nc, ny, nx, 2].
    """
    data = loadmat(filename)
    kdata_real = data['kspace_full']['real']
    kdata_imag = data['kspace_full']['imag']
    kdata_combined = np.stack((kdata_real, kdata_imag), axis=-1)
    return kdata_combined


def load_slice(kdata, time_index, slice_index):
    """
    Load and process a specific slice from k-space.

    Args:
        kdata (np.ndarray): K-space data with shape [nt, nz, nc, ny, nx, 2].
        time_index (int): Index of the time frame.
        slice_index (int): Index of the slice.

    Returns:
        np.ndarray: Processed image for the specific slice.
    """
    # Select specific slice and time frame
    kdata_slice = kdata[time_index, slice_index, :, :, :, :]  # Shape: [nc, ny, nx, 2]

    # Convert to complex
    kdata_complex = kdata_slice[..., 0] + 1j * kdata_slice[..., 1]

    # Perform IFFT and RSS for this slice
    image_space = np.fft.ifftshift(
        np.fft.ifft2(np.fft.fftshift(kdata_complex, axes=(-2, -1)), axes=(-2, -1)),
        axes=(-2, -1)
    )
    rss_image = np.sqrt(np.sum(np.abs(image_space) ** 2, axis=0))

    return rss_image
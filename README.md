# dynamic-mri-viewer

## Overview
This project aims to build an interactive viewer for **Cardiac MRI (CMR) images** that visualizes the heart over time. The primary goal is to visualize **2D slices of the heart in real-time**, showing the cardiac cycle (heart beating), with the future potential of integrating **3D+t (3D + time)** visualizations and segmentation models. The application will be built in **C++** using **Qt** for the GUI and **OpenCV** for image processing.

### Key Features
1. **2D+t Visualization**: Visualize 2D slices of the heart from CMR images in time (showing the beating heart).
2. **GUI Interface**: Provide an interactive GUI to scroll through time, adjust slices, and explore various spatial views (axial, sagittal, coronal).
3. **3D+t Expansion**: In later phases, expand to 3D+t visualizations, providing a volumetric view of the heart's motion over time.
4. **Efficient Playback**: Handle large CMR datasets efficiently to ensure smooth time-based visualization.
5. **Future Segmentation Integration**: Set up the infrastructure for future integration of segmentation algorithms to display segmented structures of the heart in 3D+t.

---

## Project Roadmap

### Phase 1: Initial Viewer Setup
- [ ] **Basic GUI with Qt**: Set up a simple GUI window that allows the user to load and view CMR images. Add buttons for basic controls (play/pause, time slider).
- [ ] **Image Loading**: Integrate OpenCV to load CMR images (DICOM or NIfTI formats). Display 2D slices in the GUI.
- [ ] **2D+t Visualization**: Implement the ability to scroll through time-based frames of a 2D slice of the CMR scan.
- [ ] **Time Controls**: Add time-based controls (play/pause, time slider) to smoothly animate the heart over time.

### Phase 2: Advanced Visualization
- [ ] **3D+t Visualization**: Implement basic 3D visualization with the ability to scroll through the 3D volume while also visualizing time.
- [ ] **Multi-Plane Viewing**: Allow users to switch between axial, sagittal, and coronal planes.
- [ ] **Rotation and Zoom**: Add interactive features like rotating and zooming the 3D model for better exploration.

### Phase 3: Future Features
- [ ] **Segmentation**: Integrate segmentation models to extract key cardiac structures (e.g., myocardium, ventricles, and atria) from the CMR images.
- [ ] **3D Model Generation**: Use the segmented structures to build 3D models that can be animated along with the time component.
- [ ] **Export Functionality**: Allow users to export the visualized images or models as videos or image sequences.

---

## Requirements
- **C++** (standard libraries)
- **Qt** (for GUI development)
- **OpenCV** (for image processing and visualization)
- **DCMTK** or **GDCM** (for handling DICOM files) and **niftiio** (for NIfTI files)

---

## Installation and Setup
1. **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/cmr-3d-time-viewer.git
    cd cmr-3d-time-viewer
    ```

2. **Install dependencies**:
    Ensure you have Qt, OpenCV, and DCMTK or GDCM installed. For example, on Ubuntu, you can install OpenCV with:
    ```bash
    sudo apt-get install libopencv-dev
    ```

3. **Build the project**:
    Using CMake:
    ```bash
    mkdir build
    cd build
    cmake ..
    make
    ```

4. **Run the application**:
    ```bash
    ./cmr-viewer
    ```

---

## Usage
- **Load CMR Image**: Open the application and load a DICOM or NIfTI CMR image file using the "Load Image" button.
- **Time Navigation**: Use the slider or play/pause controls to navigate through the time dimension.
- **View Slices**: Switch between different spatial views (axial, coronal, sagittal) to examine the heart from different perspectives.

---

## Future Plans
- Implement 3D+t visualization for full volumetric rendering.
- Integrate segmentation models for 3D heart model generation.
- Add export functionality for saving visualized images and models.

# **Dynamic MRI Viewer**

This application is a Python-based GUI for visualizing MRI data in both **k-space** (frequency domain) and **image space** (spatial domain). It allows for the display of both the composite image and the individual coil images.

---

## **Features**
- Load and visualize large MRI datasets stored in `.mat` or `.h5` files.
- Toggle between **k-space** and **image space** visualizations for all images.
- Individual coil images displayed in separate tabs with synchronized slice and time controls.
- Interactive sliders for slice and time navigation, with real-time playback functionality.
- Proportional image resizing to prevent distortion.

---

## **Requirements**
Install the required packages:

```bash
pip install numpy PyQt5 h5py
```

---

## **How to Use**

### **1. Launch the Application**
Run the application:

```bash
python mri_viewer.py
```

### **2. Load an MRI Dataset**
- Click the `Load MRI Image` button to select a `.mat` or `.h5` file containing the MRI dataset. 
- The application expects the file to include **k-space** data with real and imaginary parts stored separately.

### **3. Data Dimensions**
Ensure your dataset is organized in the following dimension order:

[z, t, c, y, x, 2]

Here:
- `z`: Number of slices in the dataset.
- `t`: Number of time frames.
- `c`: Number of coils.
- `y`: Spatial height of the image.
- `x`: Spatial width of the image.
- `2`: Real and imaginary parts of the k-space data.

### **4. Toggle Between Visualizations**
- Use the `Switch to Image Space` button to toggle between **k-space** and **image space** views for the composite image.

### **5. View Coil Images**
- Individual coil images can be opened in new tabs by clicking on a coil image in the main grid. These tabs allow synchronized slice and time navigation.

### **6. Navigate Time and Slices**
- Use the **Time** and **Slice** sliders to explore different frames and slices of the dataset. These controls are synchronized for all views, including composite images and individual coil image tabs.

---

## **Future Improvements**
- **Data Formats**: Add support for other file formats such as NIfTI or DICOM.
- **Customize Input Shapes**: Add the ability to load different data shapes including non-dynamic images.
- **Advanced Tools**: Include region-of-interest (ROI) selection and measurements.

---


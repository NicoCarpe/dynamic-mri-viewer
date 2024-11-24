# **Dynamic MRI Viewer**

This application is a Python-based GUI for visualizing MRI data in both **k-space** (frequency domain) and **image space** (spatial domain). It supports composite image display as well as individual coil images, making it a useful tool for exploring dynamic MRI datasets.

## **Features**
- Load and visualize large MRI datasets stored in `.mat` or `.h5` files.
- Toggle between **k-space** and **image space** visualizations.
- View individual coil images in a separate tab with synchronized slice and time controls.
- Proportional image resizing to prevent distortion.

---

## **Requirements**
### **Python Packages**
- `numpy`
- `PyQt5`
- `h5py`

Install the required packages using:

```bash
pip install numpy PyQt5 h5py
```

---

## **How to Use**

### **1. Launch the Application**
Run the application by executing:

```bash
python mri_viewer.py
```

### **2. Load an MRI Dataset**
- Click the `Load MRI Image` button to select a `.mat` or `.h5` file containing the MRI dataset. 
- The application expects the file to include **k-space** data with real and imaginary parts stored separately.

### **3. Data Dimensions**
Ensure your dataset is organized in the following dimension order:

```
[z, t, c, y, x, 2]
```

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
- Check the `Show Coil Images` box to enable the "Coil Images" tab, displaying all individual coil images in a scrollable grid layout.

### **6. Navigate Time and Slices**
- Use the **Time** and **Slice** sliders to explore different frames and slices of the dataset. These controls are synchronized for both the composite image and the coil images.

---

## **Future Improvements**
- **Data Formats**: Add support for other file formats such as NIfTI or DICOM.
- **Customize Input Shapes**: Add the ability load different data shapes including non-dynamic images.
- **Advanced Tools**: Include region-of-interest (ROI) selection and measurements.

---

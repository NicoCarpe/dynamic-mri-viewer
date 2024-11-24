import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QPushButton,
    QHBoxLayout,
    QSlider,
    QTabWidget,
    QCheckBox,
    QGridLayout,
    QScrollArea,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from utils import load_kdata, load_slice


class MRIViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic MRI Viewer")
        self.setGeometry(100, 100, 1000, 800)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.layout = QVBoxLayout(self.central_widget)

        # Tab widget
        self.tab_widget = QTabWidget(self)
        self.layout.addWidget(self.tab_widget)

        # Composite image tab
        self.composite_tab = QWidget()
        self.composite_layout = QVBoxLayout(self.composite_tab)
        self.tab_widget.addTab(self.composite_tab, "Composite Image")

        # Image display
        self.image_label = QLabel("Load an MRI Image", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.composite_layout.addWidget(self.image_label, stretch=1)

        # Coil images tab
        self.coil_tab = QWidget()
        self.tab_widget.addTab(self.coil_tab, "Coil Images")

        # Scroll area for coil images
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget(self)
        self.coil_layout = QGridLayout(self.scroll_content)
        self.scroll_content.setLayout(self.coil_layout)
        self.scroll_area.setWidget(self.scroll_content)

        # Add scroll area to the coil tab
        coil_tab_layout = QVBoxLayout(self.coil_tab)
        coil_tab_layout.addWidget(self.scroll_area)

        # Initially disable the coil images tab
        self.tab_widget.setTabEnabled(1, False)

        # Control panel
        self.controls = QHBoxLayout()
        self.layout.addLayout(self.controls)

        # Load button
        self.load_button = QPushButton("Load MRI Image")
        self.load_button.clicked.connect(self.load_image)
        self.controls.addWidget(self.load_button)

        # Toggle space button
        self.switch_space_button = QPushButton("Switch to Image Space")
        self.switch_space_button.clicked.connect(self.toggle_space)
        self.switch_space_button.setEnabled(False)
        self.controls.addWidget(self.switch_space_button)

        # Show coil images checkbox
        self.show_coil_checkbox = QCheckBox("Show Coil Images")
        self.show_coil_checkbox.setChecked(False)
        self.show_coil_checkbox.stateChanged.connect(self.toggle_coil_images)
        self.controls.addWidget(self.show_coil_checkbox)

        # Sliders layout
        self.slider_layout = QHBoxLayout()
        self.layout.addLayout(self.slider_layout)

        # Slice slider
        self.slice_slider = self.create_labeled_slider("Slice", self.update_slice)
        self.slider_layout.addWidget(self.slice_slider)

        # Time slider
        self.time_slider = self.create_labeled_slider("Time", self.update_slice)
        self.slider_layout.addWidget(self.time_slider)

        # Placeholder for MRI data
        self.kdata = None
        self.nt = self.nz = self.nc = 0
        self.show_kspace = True  # Start in k-space mode

    def create_labeled_slider(self, label_text, callback):
        """
        Create a compact labeled slider widget.
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(0)  # Will be set later
        slider.valueChanged.connect(callback)
        value_label = QLabel("0")
        slider.valueChanged.connect(lambda value: value_label.setText(str(value)))

        slider_layout = QHBoxLayout()
        slider_layout.addWidget(label)
        slider_layout.addWidget(slider, stretch=1)
        slider_layout.addWidget(value_label)

        layout.addLayout(slider_layout)
        return widget

    def load_image(self):
        """
        Load an MRI file and process k-space data into image-space.
        """
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open MRI File", "", "MATLAB Files (*.mat);;All Files (*)"
        )
        if file_name:
            try:
                # Load k-space data
                self.kdata = load_kdata(file_name)

                # Set slider ranges
                self.nt, self.nz, self.nc, *_ = self.kdata.shape[:3]
                self.time_slider.findChild(QSlider).setMaximum(self.nt - 1)
                self.slice_slider.findChild(QSlider).setMaximum(self.nz - 1)
                self.switch_space_button.setEnabled(True)

                # Display the first k-space slice
                self.show_kspace = True
                self.update_slice()
                print(f"Loaded k-space data with shape: {self.kdata.shape}")
            except Exception as e:
                print(f"Failed to load image: {e}")

    def update_slice(self):
        """
        Update the displayed slice based on the current slider values.
        """
        if self.kdata is None:
            return

        time_index = self.time_slider.findChild(QSlider).value()
        slice_index = self.slice_slider.findChild(QSlider).value()

        # Update composite image
        slice_data = self.kdata[time_index, slice_index]
        if self.show_kspace:
            kspace_magnitude = np.sqrt(np.sum(slice_data[..., 0] ** 2 + slice_data[..., 1] ** 2, axis=0))
            slice_data = np.log1p(kspace_magnitude)
        else:
            slice_data = load_slice(self.kdata, time_index, slice_index)

        slice_data = (slice_data / np.max(slice_data) * 255).astype(np.uint8)
        self.display_image(self.image_label, slice_data)

        # Update coil images if visible
        if self.show_coil_checkbox.isChecked():
            self.update_coil_images(time_index, slice_index)

    def update_coil_images(self, time_index, slice_index):
        """
        Update coil images in the coil tab.
        """
        # Clear current layout
        while self.coil_layout.count():
            item = self.coil_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Display each coil's image
        for i in range(self.nc):
            coil_data = self.kdata[time_index, slice_index, i, ..., 0] + 1j * self.kdata[time_index, slice_index, i, ..., 1]
            if not self.show_kspace:
                coil_data = np.abs(np.fft.ifft2(np.fft.fftshift(coil_data)))

            coil_data = np.log1p(np.abs(coil_data)) if self.show_kspace else coil_data
            coil_data = (coil_data / np.max(coil_data) * 255).astype(np.uint8)

            coil_label = QLabel()
            self.display_image(coil_label, coil_data)
            self.coil_layout.addWidget(coil_label, i // 4, i % 4)

    def display_image(self, label, data):
        """
        Helper function to display a numpy array as an image in a QLabel.
        """
        height, width = data.shape
        qimage = QImage(data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio))

    def toggle_space(self):
        """
        Toggle between K-space and image space visualization.
        """
        self.show_kspace = not self.show_kspace
        self.switch_space_button.setText(
            "Switch to K-space" if not self.show_kspace else "Switch to Image Space"
        )
        self.update_slice()

    def toggle_coil_images(self, state):
        """
        Show or hide the coil images tab.
        """
        self.tab_widget.setTabEnabled(1, state == Qt.Checked)
        if state:
            self.update_coil_images(
                self.time_slider.findChild(QSlider).value(),
                self.slice_slider.findChild(QSlider).value(),
            )



if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MRIViewer()
    viewer.show()
    sys.exit(app.exec_())

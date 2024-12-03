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
    QSizePolicy,
    QLineEdit,
    QTabBar, 
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from utils import load_kdata, load_slice


class MRIViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic MRI Viewer")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Main layout
        self.layout = QVBoxLayout(self.central_widget)

        # Tab widget
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)  # Handle tab closing
        self.layout.addWidget(self.tab_widget)

        # Composite image tab
        self.composite_tab = QWidget()
        self.composite_layout = QVBoxLayout(self.composite_tab)
        self.tab_widget.addTab(self.composite_tab, "Composite Image")

        # Image display
        self.image_label = QLabel("Load an MRI Image", self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.composite_layout.addWidget(self.image_label, stretch=1)

        # Annotation input
        self.annotation_input = QLineEdit()
        self.annotation_input.setPlaceholderText("Add annotation (Press Enter)")
        self.annotation_input.returnPressed.connect(self.add_annotation)
        self.composite_layout.addWidget(self.annotation_input)

        # Coil images tab
        self.coil_tab = QWidget()
        self.tab_widget.addTab(self.coil_tab, "Coil Images")
        self.tab_widget.currentChanged.connect(self.on_tab_change)

        # Coil images grid layout
        self.coil_layout = QGridLayout(self.coil_tab)
        self.coil_layout.setAlignment(Qt.AlignTop)

        # Disable close buttons for the first two tabs (Composite and Coil Images)
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setTabButton(0, QTabBar.RightSide, None)
        tab_bar.setTabButton(1, QTabBar.RightSide, None)

        # Disable the coil images tab initially
        self.tab_widget.setTabEnabled(1, False)

        # Control panel
        self.controls = QHBoxLayout()
        self.layout.addLayout(self.controls)

        # Load button
        self.load_button = QPushButton("Load MRI Image")
        self.load_button.clicked.connect(self.load_image)
        self.controls.addWidget(self.load_button)

        # Save button (disabled until image loaded)
        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)  # Initially disabled
        self.controls.addWidget(self.save_button)

        # Play button (disabled until image loaded)
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setEnabled(False)  # Initially disabled
        self.controls.addWidget(self.play_button)

        # Timer for playback
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.playback_next_frame)

        # Toggle space button
        self.switch_space_button = QPushButton("Switch to Image Space")
        self.switch_space_button.clicked.connect(self.toggle_space)
        self.switch_space_button.setEnabled(False)  # Initially disabled
        self.controls.addWidget(self.switch_space_button)

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

        # Floating hover label
        self.hover_label = QLabel(self)
        self.hover_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.7); color: white; padding: 2px; border-radius: 5px;"
        )
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.hover_label.hide()




    def create_labeled_slider(self, label_text, callback):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(0)
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
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open MRI File", "", "MATLAB Files (*.mat);;All Files (*)"
        )
        if file_name:
            try:
                self.kdata = load_kdata(file_name)
                self.nt, self.nz, self.nc, *_ = self.kdata.shape[:3]
                self.time_slider.findChild(QSlider).setMaximum(self.nt - 1)
                self.slice_slider.findChild(QSlider).setMaximum(self.nz - 1)
                self.switch_space_button.setEnabled(True)
                self.save_button.setEnabled(True)  # Enable after loading
                self.play_button.setEnabled(True)  # Enable after loading
                self.tab_widget.setTabEnabled(1, True)  # Enable coil images tab
                self.update_slice()
            except Exception as e:
                print(f"Failed to load image: {e}")


    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Image", "", "PNG Files (*.png);;All Files (*)"
        )
        if file_name:
            pixmap = self.image_label.pixmap()
            if pixmap:
                pixmap.save(file_name)

    def add_annotation(self):
        text = self.annotation_input.text()
        if text:
            print(f"Annotation added: {text}")  # For demonstration purposes
            self.annotation_input.clear()

    def toggle_playback(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_button.setText("Play")
        else:
            self.timer.start(100)  # Adjust playback speed
            self.play_button.setText("Pause")

    def playback_next_frame(self):
        current_time = self.time_slider.findChild(QSlider).value()
        next_time = (current_time + 1) % self.nt
        self.time_slider.findChild(QSlider).setValue(next_time)

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

        # Update coil images in the grid
        self.update_coil_images(time_index, slice_index)

        # Update all single coil tabs
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'coil_index'):
                self.update_single_coil_tab(tab.image_label, tab.coil_index)
    

    def update_coil_images(self, time_index, slice_index):
        """
        Update coil images in the coil tab with optimized grid dimensions for vertical and horizontal spacing.
        """
        # Clear the current layout
        while self.coil_layout.count():
            item = self.coil_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Determine available space
        available_width = self.coil_tab.width()
        available_height = self.coil_tab.height()

        # Margins and spacing
        spacing = 5  # Spacing between images
        margin = 5   # Outer margin around the grid
        total_margin_width = 2 * margin + (self.nc - 1) * spacing
        total_margin_height = 2 * margin + (self.nc - 1) * spacing

        # Adjust available space for margins and spacing
        adjusted_width = available_width - total_margin_width
        adjusted_height = available_height - total_margin_height

        # Get image dimensions from the first coil image
        ny, nx = self.kdata.shape[3:5]  # Assuming shape [nt, nz, nc, ny, nx, 2]
        aspect_ratio = nx / ny  # Width-to-height ratio

        # Find optimal grid dimensions to minimize vertical whitespace
        best_rows, best_cols = None, None
        best_cell_width, best_cell_height = None, None
        min_whitespace = float('inf')

        # Iterate over possible row counts to find the best fit
        for rows in range(1, self.nc + 1):
            cols = int(np.ceil(self.nc / rows))
            cell_width = adjusted_width // cols
            cell_height = int(cell_width / aspect_ratio)

            # Ensure cells fit within the available height
            if cell_height * rows > adjusted_height:
                continue  # Skip configurations that exceed the height

            # Calculate total whitespace
            total_vertical_whitespace = adjusted_height - (cell_height * rows)
            total_horizontal_whitespace = adjusted_width - (cell_width * cols)
            whitespace = total_vertical_whitespace + total_horizontal_whitespace

            # Check if this configuration minimizes whitespace
            if whitespace < min_whitespace:
                min_whitespace = whitespace
                best_rows, best_cols = rows, cols
                best_cell_width, best_cell_height = cell_width, cell_height

        # Debugging: Log layout information
        print(f"Best grid: {best_rows}x{best_cols}, Cell size: {best_cell_width}x{best_cell_height}px")

        # Set layout spacing and margins
        self.coil_layout.setHorizontalSpacing(spacing)
        self.coil_layout.setVerticalSpacing(spacing)
        self.coil_layout.setContentsMargins(margin, margin, margin, margin)

        # Add each coil image to the grid
        for i in range(self.nc):
            coil_data = self.kdata[time_index, slice_index, i, ..., 0] + 1j * self.kdata[time_index, slice_index, i, ..., 1]
            if not self.show_kspace:
                coil_data = np.abs(np.fft.ifft2(np.fft.fftshift(coil_data)))

            coil_data = np.log1p(np.abs(coil_data)) if self.show_kspace else coil_data
            coil_data = (coil_data / np.max(coil_data) * 255).astype(np.uint8)

            # Create a QLabel for the coil image
            coil_label = self.create_coil_label(coil_data, best_cell_width, best_cell_height, i)
            self.coil_layout.addWidget(coil_label, i // best_cols, i % best_cols)

    def create_coil_label(self, coil_data, width, height, index):
        """
        Create a QLabel for a coil image with click-to-new-tab functionality.
        """
        coil_label = QLabel()
        coil_label.setFixedSize(width, height)
        self.display_image(coil_label, coil_data)

        coil_label.enterEvent = lambda event: self.show_hover_label(coil_label, f"Coil {index + 1}")
        coil_label.leaveEvent = lambda event: self.hover_label.hide()
        coil_label.mousePressEvent = lambda event: self.open_coil_in_new_tab(index)

        return coil_label


    def open_coil_in_new_tab(self, coil_index):
        """
        Open a specific coil image in a new tab and use global sliders for navigation.
        """
        # Check if the tab already exists
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == f"Coil {coil_index + 1}":
                self.tab_widget.setCurrentIndex(i)
                return

        # Create a new tab
        new_tab = QWidget()
        new_layout = QVBoxLayout(new_tab)

        # Image display
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignCenter)
        new_layout.addWidget(image_label, stretch=1)

        # Add the new tab to the tab widget
        self.tab_widget.addTab(new_tab, f"Coil {coil_index + 1}")
        self.tab_widget.setCurrentWidget(new_tab)

        # Update the image for the current coil
        self.update_single_coil_tab(image_label, coil_index)

        # Store reference to the image_label for the coil tab
        new_tab.image_label = image_label
        new_tab.coil_index = coil_index  # Attach the coil index for this tab

    def get_coil_image_data(self, time_index, slice_index, coil_index):
        """
        Fetch data for a specific coil image at the given time and slice indices.
        """
        coil_data = self.kdata[time_index, slice_index, coil_index, ..., 0] + \
                    1j * self.kdata[time_index, slice_index, coil_index, ..., 1]
        if not self.show_kspace:
            coil_data = np.abs(np.fft.ifft2(np.fft.fftshift(coil_data)))

        coil_data = np.log1p(np.abs(coil_data)) if self.show_kspace else coil_data
        coil_data = (coil_data / np.max(coil_data) * 255).astype(np.uint8)
        return coil_data

    def update_single_coil_tab(self, image_label, coil_index):
        """
        Update the displayed image for a specific coil tab using global sliders.
        """
        time_index = self.time_slider.findChild(QSlider).value()
        slice_index = self.slice_slider.findChild(QSlider).value()

        coil_data = self.get_coil_image_data(time_index, slice_index, coil_index)
        self.display_image(image_label, coil_data)

    def close_tab(self, index):
        """
        Handle tab closing. Prevent closing Composite and Coil Images tabs.
        """
        if index > 1:  # Prevent closing Composite or Coil Images tabs
            self.tab_widget.removeTab(index)

    def show_hover_label(self, widget, text):
        """
        Display a floating hover label at the top left of the respective coil image.
        """
        self.hover_label.setText(text)
        self.hover_label.adjustSize()

        # Position the label at the top-left corner of the widget
        pos = widget.mapToGlobal(widget.rect().topLeft())
        self.hover_label.move(pos.x() + 5, pos.y() + 5)  # Small offset for visibility
        self.hover_label.show()

    def resizeEvent(self, event):
        """
        Handle window resize events to adjust layouts and update content.
        """
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.composite_tab:
            # Composite tab resizing
            self.update_slice()
        elif current_tab == self.coil_tab:
            # Multicoil grid resizing
            self.update_coil_images(
                self.time_slider.findChild(QSlider).value(),
                self.slice_slider.findChild(QSlider).value()
            )
        elif hasattr(current_tab, 'image_label'):
            # Specific coil tab resizing
            self.update_single_coil_tab(current_tab.image_label, current_tab.coil_index)

        super().resizeEvent(event)  # Call the base class implementation


    def display_image(self, label, data):
        height, width = data.shape
        qimage = QImage(data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio))

    def toggle_space(self):
        """
        Toggle between k-space and image space and update all relevant displays.
        """
        self.show_kspace = not self.show_kspace
        self.switch_space_button.setText(
            "Switch to K-space" if not self.show_kspace else "Switch to Image Space"
        )
        self.update_slice()

    def on_tab_change(self, index):
        """
        Handle tab switch events and update the content for the current tab.
        """
        if index == -1:
            return  # No tab selected

        current_tab = self.tab_widget.widget(index)
        if current_tab == self.composite_tab:
            # Update the composite image view
            self.update_slice()
        elif current_tab == self.coil_tab:
            # Update the multicoil grid view
            self.update_coil_images(
                self.time_slider.findChild(QSlider).value(),
                self.slice_slider.findChild(QSlider).value()
            )
        elif hasattr(current_tab, 'coil_index'):
            # Update the specific coil view
            self.update_single_coil_tab(current_tab.image_label, current_tab.coil_index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MRIViewer()
    viewer.show()
    sys.exit(app.exec_())

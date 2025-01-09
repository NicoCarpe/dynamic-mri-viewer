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
    QGridLayout,
    QLineEdit,
    QTabBar
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage

# Utilities: load_kdata, load_slice, etc.
from utils import load_kdata, load_slice  # You can remove make_3d_volume, numpy_to_vtk_image if no longer needed.

# Zoom/Pan composite view
from zoom_pan import ZoomPanGraphicsView


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

        # ----------------
        # 1) Composite Image Tab
        # ----------------
        self.composite_tab = QWidget()
        self.composite_layout = QVBoxLayout(self.composite_tab)
        self.tab_widget.addTab(self.composite_tab, "Composite Image")

        # Zoom/pan composite view
        self.image_view = ZoomPanGraphicsView()
        self.composite_layout.addWidget(self.image_view, stretch=1)

        # Annotation input
        self.annotation_input = QLineEdit()
        self.annotation_input.setPlaceholderText("Add annotation (Press Enter)")
        self.annotation_input.returnPressed.connect(self.add_annotation)
        self.composite_layout.addWidget(self.annotation_input)

        # ----------------
        # 2) Coil Images Tab
        # ----------------
        self.coil_tab = QWidget()
        self.tab_widget.addTab(self.coil_tab, "Coil Images")
        self.tab_widget.currentChanged.connect(self.on_tab_change)
        self.coil_layout = QGridLayout(self.coil_tab)
        self.coil_layout.setAlignment(Qt.AlignTop)

        # Disable close buttons for the first two tabs (Composite & Coil Images)
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setTabButton(0, QTabBar.RightSide, None)  # Composite
        tab_bar.setTabButton(1, QTabBar.RightSide, None)  # Coil Images

        # Disable the coil images tab initially
        self.tab_widget.setTabEnabled(1, False)

        # Control panel (Load, Save, Play, etc.)
        self.controls = QHBoxLayout()
        self.layout.addLayout(self.controls)

        self.load_button = QPushButton("Load MRI Image")
        self.load_button.clicked.connect(self.load_image)
        self.controls.addWidget(self.load_button)

        self.save_button = QPushButton("Save Image")
        self.save_button.clicked.connect(self.save_image)
        self.save_button.setEnabled(False)
        self.controls.addWidget(self.save_button)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setEnabled(False)
        self.controls.addWidget(self.play_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.playback_next_frame)

        self.switch_space_button = QPushButton("Switch to Image Space")
        self.switch_space_button.clicked.connect(self.toggle_space)
        self.switch_space_button.setEnabled(False)
        self.controls.addWidget(self.switch_space_button)

        # Sliders (slice, time)
        self.slider_layout = QHBoxLayout()
        self.layout.addLayout(self.slider_layout)

        self.slice_slider = self.create_labeled_slider("Slice", self.update_slice)
        self.slider_layout.addWidget(self.slice_slider)

        self.time_slider = self.create_labeled_slider("Time", self.update_slice)
        self.slider_layout.addWidget(self.time_slider)

        # MRI data placeholders
        self.kdata = None
        self.nt = self.nz = self.nc = 0
        self.show_kspace = True  # Start in k-space mode

        # Hover label
        self.hover_label = QLabel(self)
        self.hover_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.7); color: white; padding: 2px; border-radius: 5px;"
        )
        self.hover_label.setAlignment(Qt.AlignCenter)
        self.hover_label.hide()

    def create_labeled_slider(self, label_text, callback):
        w = QWidget()
        layout = QHBoxLayout(w)
        lbl = QLabel(label_text)
        sldr = QSlider(Qt.Horizontal)
        sldr.setMinimum(0)
        sldr.setMaximum(0)
        sldr.valueChanged.connect(callback)
        val_lbl = QLabel("0")
        sldr.valueChanged.connect(lambda v: val_lbl.setText(str(v)))
        layout.addWidget(lbl)
        layout.addWidget(sldr, stretch=1)
        layout.addWidget(val_lbl)
        return w

    def load_image(self):
        """Load .mat file containing k-space data, then show it."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open MRI File", "", "MATLAB Files (*.mat);;All Files (*)"
        )
        if file_name:
            try:
                self.kdata = load_kdata(file_name)  # shape [nt, nz, nc, ny, nx, 2]
                self.nt, self.nz, self.nc, *_ = self.kdata.shape[:3]

                # Enable buttons
                self.switch_space_button.setEnabled(True)
                self.save_button.setEnabled(True)
                self.play_button.setEnabled(True)
                self.tab_widget.setTabEnabled(1, True)

                # Update the slice/time sliders
                self.time_slider.findChild(QSlider).setMaximum(self.nt - 1)
                self.slice_slider.findChild(QSlider).setMaximum(self.nz - 1)

                # Possibly reset coil grid layout
                if hasattr(self, 'grid_rows'):
                    del self.grid_rows
                    del self.grid_cols

                # Update 2D composite view
                self.update_slice()

            except Exception as e:
                print(f"Failed to load image: {e}")

    def save_image(self):
        """Save the current composite image (QGraphicsView)."""
        if not self.image_view.image_item:
            return
        pixmap = self.image_view.image_item.pixmap()
        if pixmap and not pixmap.isNull():
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", "PNG Files (*.png);;All Files (*)"
            )
            if file_name:
                pixmap.save(file_name)

    def add_annotation(self):
        text = self.annotation_input.text()
        if text:
            print(f"Annotation added: {text}")
            self.annotation_input.clear()

    def toggle_playback(self):
        if self.timer.isActive():
            self.timer.stop()
            self.play_button.setText("Play")
        else:
            self.timer.start(100)
            self.play_button.setText("Pause")

    def playback_next_frame(self):
        current_time = self.time_slider.findChild(QSlider).value()
        next_time = (current_time + 1) % self.nt
        self.time_slider.findChild(QSlider).setValue(next_time)

    def update_slice(self):
        """Update the 2D composite image plus coil images based on slice/time."""
        if self.kdata is None:
            return

        time_idx = self.time_slider.findChild(QSlider).value()
        slice_idx = self.slice_slider.findChild(QSlider).value()

        # Composite image data
        slice_data = self.kdata[time_idx, slice_idx]
        if self.show_kspace:
            kmag = np.sqrt(np.sum(slice_data[..., 0]**2 + slice_data[..., 1]**2, axis=0))
            slice_data = np.log1p(kmag)
        else:
            slice_data = load_slice(self.kdata, time_idx, slice_idx)

        slice_data = (slice_data / (slice_data.max() + 1e-9) * 255).astype(np.uint8)
        self.display_composite_image(slice_data)

        # Update coil grid
        self.update_coil_images(time_idx, slice_idx)

        # Update single-coil tabs
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'coil_index'):
                self.update_single_coil_tab(tab.image_label, tab.coil_index)

    def display_composite_image(self, array_2d: np.ndarray):
        """Show a 2D NumPy array in the composite ZoomPanGraphicsView."""
        h, w = array_2d.shape
        qimage = QImage(array_2d, w, h, w, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        self.image_view.set_pixmap(pixmap)

    def update_coil_images(self, time_index, slice_index):
        """Fill the coil tab with nc coil images in a grid."""
        if not hasattr(self, 'grid_rows') or not hasattr(self, 'grid_cols'):
            available_width = self.coil_tab.width()
            available_height = self.coil_tab.height()
            margin, spacing = 5, 5

            total_margin_w = 2 * margin + (self.nc - 1) * spacing
            total_margin_h = 2 * margin + (self.nc - 1) * spacing
            adj_w = available_width - total_margin_w
            adj_h = available_height - total_margin_h

            ny, nx = self.kdata.shape[3:5]  # [nt, nz, nc, ny, nx, 2]
            aspect_ratio = nx / ny

            import math
            min_whitespace = float('inf')
            for rows in range(1, self.nc + 1):
                cols = math.ceil(self.nc / rows)
                cell_w = adj_w // cols
                cell_h = int(cell_w / aspect_ratio)
                if cell_h * rows <= adj_h:
                    whitespace = (adj_h - cell_h * rows) + (adj_w - cell_w * cols)
                    if whitespace < min_whitespace:
                        min_whitespace = whitespace
                        self.grid_rows, self.grid_cols = rows, cols
                        self.cell_width, self.cell_height = cell_w, cell_h

            print(f"Grid computed: {self.grid_rows}x{self.grid_cols}, "
                  f"Cell size: {self.cell_width}x{self.cell_height}px")

        while self.coil_layout.count():
            item = self.coil_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for i in range(self.nc):
            coil_data = (self.kdata[time_index, slice_index, i, ..., 0]
                         + 1j * self.kdata[time_index, slice_index, i, ..., 1])
            if not self.show_kspace:
                coil_data = np.abs(np.fft.ifft2(np.fft.fftshift(coil_data)))
            coil_data = np.log1p(np.abs(coil_data)) if self.show_kspace else coil_data
            coil_data = coil_data / (coil_data.max() + 1e-9) * 255
            coil_data = coil_data.astype(np.uint8)

            coil_label = self.create_coil_label(coil_data, self.cell_width, self.cell_height, i)
            self.coil_layout.addWidget(coil_label, i // self.grid_cols, i % self.grid_cols)

    def create_coil_label(self, coil_data, w, h, index):
        lbl = QLabel()
        lbl.setFixedSize(w, h)
        self.display_on_label(lbl, coil_data)
        lbl.enterEvent = lambda e: self.show_hover_label(lbl, f"Coil {index+1}")
        lbl.leaveEvent = lambda e: self.hover_label.hide()
        lbl.mousePressEvent = lambda e: self.open_coil_in_new_tab(index)
        return lbl

    def display_on_label(self, label: QLabel, array_2d: np.ndarray):
        hh, ww = array_2d.shape
        qimage = QImage(array_2d, ww, hh, ww, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        label.setPixmap(pixmap.scaled(label.width(), label.height(), Qt.KeepAspectRatio))

    def open_coil_in_new_tab(self, coil_index):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == f"Coil {coil_index+1}":
                self.tab_widget.setCurrentIndex(i)
                return

        new_tab = QWidget()
        new_layout = QVBoxLayout(new_tab)
        img_label = QLabel()
        img_label.setAlignment(Qt.AlignCenter)
        new_layout.addWidget(img_label, stretch=1)

        self.tab_widget.addTab(new_tab, f"Coil {coil_index+1}")
        self.tab_widget.setCurrentWidget(new_tab)

        new_tab.image_label = img_label
        new_tab.coil_index = coil_index
        self.update_single_coil_tab(img_label, coil_index)

    def get_coil_image_data(self, t, s, coil_i):
        data = (self.kdata[t, s, coil_i, ..., 0]
                + 1j * self.kdata[t, s, coil_i, ..., 1])
        if not self.show_kspace:
            data = np.abs(np.fft.ifft2(np.fft.fftshift(data)))
        data = np.log1p(np.abs(data)) if self.show_kspace else data
        data = data / (data.max() + 1e-9) * 255
        return data.astype(np.uint8)

    def update_single_coil_tab(self, label, coil_i):
        t = self.time_slider.findChild(QSlider).value()
        s = self.slice_slider.findChild(QSlider).value()
        coil_array = self.get_coil_image_data(t, s, coil_i)
        self.display_on_label(label, coil_array)

    def close_tab(self, index):
        # Prevent closing Composite (0) and Coil Images (1).
        if index > 1:
            self.tab_widget.removeTab(index)

    def show_hover_label(self, widget, text):
        self.hover_label.setText(text)
        self.hover_label.adjustSize()
        pos = widget.mapToGlobal(widget.rect().topLeft())
        self.hover_label.move(pos.x() + 5, pos.y() + 5)
        self.hover_label.show()

    def resizeEvent(self, event):
        current_tab = self.tab_widget.currentWidget()
        if current_tab == self.composite_tab:
            self.update_slice()
        elif current_tab == self.coil_tab:
            if hasattr(self, 'grid_rows'):
                del self.grid_rows
                del self.grid_cols
            self.update_coil_images(
                self.time_slider.findChild(QSlider).value(),
                self.slice_slider.findChild(QSlider).value()
            )
        elif hasattr(current_tab, 'image_label'):
            self.update_single_coil_tab(current_tab.image_label, current_tab.coil_index)
        super().resizeEvent(event)

    def toggle_space(self):
        self.show_kspace = not self.show_kspace
        txt = "Switch to K-space" if not self.show_kspace else "Switch to Image Space"
        self.switch_space_button.setText(txt)
        self.update_slice()

    def on_tab_change(self, index):
        if index == -1:
            return
        current_tab = self.tab_widget.widget(index)
        if current_tab == self.composite_tab:
            self.update_slice()
        elif current_tab == self.coil_tab:
            if hasattr(self, 'grid_rows'):
                del self.grid_rows
                del self.grid_cols
            self.update_coil_images(
                self.time_slider.findChild(QSlider).value(),
                self.slice_slider.findChild(QSlider).value()
            )
        elif hasattr(current_tab, 'coil_index'):
            self.update_single_coil_tab(current_tab.image_label, current_tab.coil_index)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MRIViewer()
    viewer.show()
    sys.exit(app.exec_())

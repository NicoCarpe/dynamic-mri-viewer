from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QPixmap, QMouseEvent

class ZoomPanGraphicsView(QGraphicsView):
    """
    A custom QGraphicsView for zoom/pan and optional ROI selection.
    Right-click toggles between ScrollHandDrag and RubberBandDrag.
    """
    roiSelected = pyqtSignal(QRectF)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.image_item = None
        self._zoom_factor = 1.25
        self.setDragMode(QGraphicsView.NoDrag)
        self._had_pixmap_before = False

    def set_pixmap_item(self, item):
        """
        Set the QGraphicsPixmapItem that we will be displaying.
        (We could create the pixmap item ourselves; 
         or the caller can pass one in, e.g. self.image_item.)
        """
        if self.image_item is not None:
            self.scene().removeItem(self.image_item)

        self.image_item = item
        self.scene().addItem(self.image_item)

        if not self._had_pixmap_before:
            # Fit only the first time, or on a 'reset view' action
            self.fitInView(self.image_item, Qt.KeepAspectRatio)
            self._had_pixmap_before = True

    def set_pixmap(self, pixmap: QPixmap):
        """Replaces the displayed pixmap, preserving the current zoom if desired."""
        if self.image_item is None:
            # We create a new QGraphicsPixmapItem if it doesn't exist yet
            self.image_item = QGraphicsPixmapItem()
            self.scene().addItem(self.image_item)

        self.image_item.setPixmap(pixmap)

        # Optional: if you want to auto-fit on the first assignment
        if not self._had_pixmap_before:
            self.fitInView(self.image_item, Qt.KeepAspectRatio)
            self._had_pixmap_before = True

    def reset_view(self):
        """
        Public method to let the user reset the current zoom/pan to fit the image.
        """
        if self.image_item:
            self.fitInView(self.image_item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        """Zoom in/out with the mouse wheel."""
        if self.image_item and not self.image_item.pixmap().isNull():
            if event.angleDelta().y() > 0:
                zoom_factor = self._zoom_factor
            else:
                zoom_factor = 1 / self._zoom_factor
            self.scale(zoom_factor, zoom_factor)
            event.accept()
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        # Right click toggles drag modes (demo behavior)
        if event.button() == Qt.RightButton:
            if self.dragMode() == QGraphicsView.ScrollHandDrag:
                self.setDragMode(QGraphicsView.RubberBandDrag)
            else:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        # If using RubberBandDrag, we can emit a signal for the selected ROI
        if self.dragMode() == QGraphicsView.RubberBandDrag:
            rubber_band_rect = self.rubberBandRect()
            if not rubber_band_rect.isNull():
                scene_rect = self.mapToScene(rubber_band_rect).boundingRect()
                self.roiSelected.emit(scene_rect)
        super().mouseReleaseEvent(event)

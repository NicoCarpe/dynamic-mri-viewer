import sys
from PyQt5.QtWidgets import QApplication
from mri_viewer import MRIViewer

def main():
    app = QApplication(sys.argv)
    viewer = MRIViewer()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
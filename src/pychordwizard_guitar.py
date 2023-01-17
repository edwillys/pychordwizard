from PyQt5 import QtWidgets
from fretboard_widget import FretboardView
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    w = QtWidgets.QWidget()

    lay_main = QtWidgets.QHBoxLayout(w)

    fretboard = FretboardView()
    fretboard.setOpenBottom(True)
    lay_main.addWidget(fretboard)

    lay_right = QtWidgets.QVBoxLayout(w)
    lay_grid = QtWidgets.QGridLayout(w)
    lay_grid.addWidget(QtWidgets.QLabel("Number of strings"), 0, 0)
    lay_grid.addWidget(QtWidgets.QComboBox(), 0, 1)
    lay_grid.addWidget(QtWidgets.QLabel("Tuning"), 1, 0)
    lay_grid.addWidget(QtWidgets.QComboBox(), 1, 1)
    lay_grid.addWidget(QtWidgets.QLabel("Chord Name"), 2, 0)
    lay_grid.addWidget(QtWidgets.QLineEdit(), 2, 1)
    lay_grid.setRowStretch(0, 0)
    lay_grid.setRowStretch(1, 0)
    lay_right.addLayout(lay_grid)
    lay_right.addSpacerItem(QtWidgets.QSpacerItem(
        0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
    lay_main.addLayout(lay_right)

    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())

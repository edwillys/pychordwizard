from PyQt5 import QtWidgets
from fretboard_widget import FretboardView
import sys


class PyChordWizardGuitar(QtWidgets.QWidget):
    NUM_STRINGS_TUNING_MAP = {
        "6": {
            "Standard": "E-A-D-G-B-E",
            "Drop D": "D-A-D-G-B-E",
            "Open D": "D-A-D-G-B-D",
        },
        "7": {
            "Standard": "B-E-A-D-G-B-E"
        },
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        lay_main = QtWidgets.QHBoxLayout(self)

        self.fretboard = FretboardView()
        self.fretboard.setOpenBottom(True)
        lay_main.addWidget(self.fretboard)

        lay_right = QtWidgets.QVBoxLayout()
        lay_grid = QtWidgets.QGridLayout()

        lay_grid.addWidget(QtWidgets.QLabel("Number of strings"), 0, 0)
        self.cb_num_strings = QtWidgets.QComboBox()
        for num_string in self.NUM_STRINGS_TUNING_MAP:
            self.cb_num_strings.addItem(num_string)
        self.cb_num_strings.setCurrentIndex(0)
        self.cb_num_strings.currentIndexChanged.connect(
            self.onNumStringsChanged)
        lay_grid.addWidget(self.cb_num_strings, 0, 1)

        lay_grid.addWidget(QtWidgets.QLabel("Tuning"), 1, 0)
        self.cb_tuning = QtWidgets.QComboBox()
        lay_grid.addWidget(self.cb_tuning, 1, 1)
        self.cb_tuning.currentIndexChanged.connect(self.onTuningChanged)
        self.updateTunings()

        lay_grid.addWidget(QtWidgets.QLabel("Capo"), 2, 0)
        self.cb_capo = QtWidgets.QSpinBox()
        self.cb_capo.setValue(0)
        self.cb_capo.setMinimum(0)
        self.cb_capo.setMaximum(12)
        lay_grid.addWidget(self.cb_capo, 2, 1)
        self.cb_capo.valueChanged.connect(self.onCapoChanged)

        lay_grid.addWidget(QtWidgets.QLabel("Chord Name"), 3, 0)
        lay_grid.addWidget(QtWidgets.QLineEdit(), 3, 1)

        lay_grid.setRowStretch(0, 0)
        lay_grid.setRowStretch(1, 0)
        lay_right.addLayout(lay_grid)
        #
        lay_buttons = QtWidgets.QGridLayout()
        lay_buttons.addWidget(QtWidgets.QPushButton("Alt"), 0, 0)
        lay_buttons.addWidget(QtWidgets.QPushButton("Alt"), 0, 1)
        lay_buttons.addWidget(QtWidgets.QPushButton("Alt"), 0, 2)
        lay_buttons.addWidget(QtWidgets.QPushButton("Alt"), 1, 0)
        lay_buttons.addWidget(QtWidgets.QPushButton("Alt"), 1, 1)
        lay_buttons.addWidget(QtWidgets.QPushButton("Alt"), 1, 2)
        lay_right.addLayout(lay_buttons)
        # vertical spacer
        lay_right.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        lay_main.addLayout(lay_right)

    def onNumStringsChanged(self):
        self.updateTunings()

    def onCapoChanged(self):
        capo = self.cb_capo.value()
        self.fretboard.setCapo(capo)

    def onTuningChanged(self):
        tuning = self.cb_tuning.currentText()
        if tuning:
            tuning = tuning.split()[0]
            tuning_array = [note for note in tuning.split("-")]
            self.fretboard.setTuning(tuning_array)

    def updateTunings(self):
        num_strings = self.cb_num_strings.currentText()
        self.cb_tuning.clear()
        tuning = self.NUM_STRINGS_TUNING_MAP[num_strings]
        for key, val in tuning.items():
            self.cb_tuning.addItem(f"{val} ({key})")
        self.cb_tuning.setCurrentIndex(0)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    w = PyChordWizardGuitar()
    w.resize(640, 640)
    w.show()
    sys.exit(app.exec_())

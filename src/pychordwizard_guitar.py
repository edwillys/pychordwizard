from PyQt5 import QtWidgets
from fretboard_widget import FretboardView
from chord import Chord
from note import Note
import sys


class PyChordWizardGuitar(QtWidgets.QMainWindow):
    NUM_STRINGS_TUNING_MAP = {
        "6": {
            "Standard": "E-A-D-G-B-E",
            "Drop D": "D-A-D-G-B-E",
            "Open D": "D-A-D-F#-A-D",
        },
        "7": {
            "Standard": "B-E-A-D-G-B-E"
        },
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.active_notes = []
        self.chord_name_items = []

        lay_main = QtWidgets.QHBoxLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(lay_main)
        self.setCentralWidget(widget)
        self.setWindowTitle("PyChordWizard Guitar")

        # Fretboard
        self.fretboard = FretboardView()
        self.fretboard.setOpenBottom(True)
        self.fretboard.scene().notes_changed.connect(self.onNotesChanged)
        lay_main.addWidget(self.fretboard)

        lay_right = QtWidgets.QVBoxLayout()
        lay_grid = QtWidgets.QGridLayout()

        # String number combobox
        lay_grid.addWidget(QtWidgets.QLabel("Number of strings"), 0, 0)
        self.cb_num_strings = QtWidgets.QComboBox()
        for num_string in self.NUM_STRINGS_TUNING_MAP:
            self.cb_num_strings.addItem(num_string)
        self.cb_num_strings.setCurrentIndex(0)
        self.cb_num_strings.currentIndexChanged.connect(
            self.onNumStringsChanged)
        lay_grid.addWidget(self.cb_num_strings, 0, 1)

        # Tuning combobox
        lay_grid.addWidget(QtWidgets.QLabel("Tuning"), 1, 0)
        self.cb_tuning = QtWidgets.QComboBox()
        lay_grid.addWidget(self.cb_tuning, 1, 1)
        self.cb_tuning.currentIndexChanged.connect(self.onTuningChanged)
        self.updateTunings()

        # Capo spin box
        lay_grid.addWidget(QtWidgets.QLabel("Capo"), 2, 0)
        self.cb_capo = QtWidgets.QSpinBox()
        self.cb_capo.setValue(0)
        self.cb_capo.setMinimum(0)
        self.cb_capo.setMaximum(12)
        lay_grid.addWidget(self.cb_capo, 2, 1)
        self.cb_capo.valueChanged.connect(self.onCapoChanged)

        lay_right.addLayout(lay_grid)
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        lay_right.addWidget(separator)

        # Chord names
        self.lay_chord_names = QtWidgets.QGridLayout()
        lay_right.addLayout(self.lay_chord_names)
        # vertical spacer
        lay_right.addSpacerItem(QtWidgets.QSpacerItem(
            0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        lay_main.addLayout(lay_right)

        # File menu
        menubar = QtWidgets.QMenuBar()
        menu_file = menubar.addMenu("File")
        action_file_clear = QtWidgets.QAction("Clear", self)
        action_file_clear.setShortcut("Ctrl+K")
        action_file_clear.triggered.connect(self.onClear)
        menu_file.addAction(action_file_clear)
        menubar.addMenu(menu_file)

        self.setMenuBar(menubar)

    def onNumStringsChanged(self) -> None:
        self.updateTunings()

    def onCapoChanged(self) -> None:
        capo = self.cb_capo.value()
        self.fretboard.setCapo(capo)
        self.updateChordName()

    def onTuningChanged(self) -> None:
        tuning = self.cb_tuning.currentText()
        if tuning:
            # get the notes for each string
            tuning = tuning.split()[0]
            tuning_array = [note for note in tuning.split("-")]
            self.fretboard.setTuning(list(tuning_array))
            # now add the octaves, starting from the highest string,
            # which is in octave 4 if above 'C4' or octave 3 if below it
            tuning_array.reverse()
            if tuning_array[0] >= 'C':
                tuning_array[0] += "4"
            else:
                tuning_array[0] += "3"
            self.string_notes = [Note(tuning_array[0])]

            for i in range(len(tuning_array) - 1):
                note = self.string_notes[i]
                next_note = Note(tuning_array[i+1])
                self.string_notes += [note.find_below(next_note)]
            self.string_notes.reverse()

    def onNotesChanged(self, active_notes: dict[int, int]) -> None:
        self.active_notes = active_notes
        self.updateChordName()

    def onClear(self) -> None:
        self.fretboard.clear()

    def updateTunings(self) -> None:
        num_strings = self.cb_num_strings.currentText()
        self.cb_tuning.clear()
        tuning = self.NUM_STRINGS_TUNING_MAP[num_strings]
        for key, val in tuning.items():
            self.cb_tuning.addItem(f"{val} ({key})")
        self.cb_tuning.setCurrentIndex(0)

    def updateChordName(self) -> None:
        for item in self.chord_name_items:
            self.lay_chord_names.removeWidget(item)
        self.chord_name_items = []

        if self.active_notes:
            notes = set()
            for key, val in self.active_notes.items():
                note = self.string_notes[key] + val + self.cb_capo.value()
                notes.add(note)
            chord = Chord(notes)

            n_cols = 2
            # eliminate name duplicates by using dict(). set() does not keep the order
            chord_names = dict()
            for var in chord.variants:
                chord_names[str(var)] = None
            for i, name in enumerate(chord_names):
                item = QtWidgets.QPushButton(str(name))
                self.chord_name_items += [item]
                self.lay_chord_names.addWidget(item, i // n_cols, i % n_cols)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    w = PyChordWizardGuitar()
    w.resize(640, 640)
    w.show()
    sys.exit(app.exec_())

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsTextItem, QGraphicsLineItem
from PyQt5.QtCore import QPointF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPen, QBrush, QTransform, QFont
from fretboard_items import FretboardBarreItem, FretboardNoteItem, \
    FretboardInlayItem, StringButtonItem, FretboardItem


class FretboardScene(QGraphicsScene):
    barre_pressed = pyqtSignal(int, tuple)
    existing_note_pressed = pyqtSignal(int, int)
    new_note_pressed = pyqtSignal(int, int)
    notes_changed = pyqtSignal(dict)


class FretboardView(QtWidgets.QGraphicsView):
    FRETWIDTH, FRETHEIGHT = 20, 25
    NOTEDIAMETER = 7
    BARRE_THICKNESS = NOTEDIAMETER
    STRING_BTN_SITZE = 5

    def __init__(self, num_frets=13, tuning: list[str] = ["E", "A", "D", "G", "B", "E"], fret_start=0, parent=None) -> None:
        super().__init__(parent)
        # self.initialize()

        self.fret_start = fret_start
        self.num_frets = num_frets
        self.num_strings = len(tuning)
        self.tuning = tuning
        self.note_items = {}
        self.barre_items = {}
        self.active = {}
        self.moving_barre_item = None
        self.note_pressed_coord = None
        self.moving_barre_string_coord = None
        self.moving_barre_fret = None
        self.open_top = False
        self.open_bottom = True

        # set up scene
        scene = FretboardScene()
        self.setScene(scene)

        self.initGui()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)

    def sizeHint(self):
        return self.mapFromScene(self.sceneRect()).boundingRect().size()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        Deal with the barres when the cursor has been pressed and is moving around
        """
        # barre should only be drawn if a the cursor is moving over the fretboard
        # or the barre itself. Thus, we check the intersected item
        if not self.note_pressed_coord:
            return
        sp = self.mapToScene(event.pos())
        item = self.scene().itemAt(sp, QTransform())
        if item and (isinstance(item, FretboardItem) or isinstance(item, FretboardBarreItem)):
            np_fret, np_string = self.note_pressed_coord
            string = int((sp.x() + self.FRETWIDTH / 2) / self.FRETWIDTH)

            if string == np_string:
                # the barre is reduced to a single note: delete the current barre if any
                # and generate a note
                if self.moving_barre_item:
                    self.scene().removeItem(self.moving_barre_item)
                    self.moving_barre_item = None
                    self.moving_barre_string_coord = None
                    self.moving_barre_fret = None
                self.addSingleNote((np_fret, string))
            else:
                # We're in barre mode: check if we need to create one,  extend it or shrink it
                # Extension or reduction only happens if the string index is different than
                # the last barre string.
                string_coord = (np_string, string)
                if self.moving_barre_string_coord != string_coord:
                    self.moving_barre_fret = np_fret
                    self.moving_barre_string_coord = string_coord

                    # we delete the old barre before generating the new one
                    if self.moving_barre_item:
                        self.scene().removeItem(self.moving_barre_item)

                    # check if the barre intersects with any notes and overwrite them (delete the notes)
                    coords_to_delete = []
                    leftmost_string, rightmost_string = sorted(
                        self.moving_barre_string_coord)
                    for note_fret, np_string in self.note_items:
                        if (note_fret == self.moving_barre_fret or note_fret == 0) \
                                and np_string >= leftmost_string \
                                and np_string <= rightmost_string:
                            coords_to_delete += [(note_fret, np_string)]

                    for coord in coords_to_delete:
                        self.removeSingleNote(coord)

                    (x, y, w, h) = self.calculateBarreRect(
                        np_fret, self.moving_barre_string_coord
                    )

                    self.moving_barre_item = FretboardBarreItem(
                        self.moving_barre_fret, self.moving_barre_string_coord, x, y + self.y_offset, w, h
                    )

                    self.scene().addItem(self.moving_barre_item)
                    self.updateActiveStringsAndNotes()

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.moving_barre_item and self.moving_barre_string_coord and self.moving_barre_fret:
            self.addBarreItem(
                self.moving_barre_fret, self.moving_barre_string_coord, self.moving_barre_item)

        self.moving_barre_fret = None
        self.moving_barre_string_coord = None
        self.moving_barre_item = None
        self.note_pressed_coord = None

        return super().mouseReleaseEvent(event)

    @pyqtSlot(int, int)
    def onNewNotePressed(self, fret: int, string: int):
        self.note_pressed_coord = (fret, string)
        self.addSingleNote(self.note_pressed_coord)

    @pyqtSlot(int, tuple)
    def onBarrePressed(self, fret: int, string_coords: tuple[int, int]):
        self.removeBarreItem(fret, string_coords)

    @pyqtSlot(int, int)
    def onExistingNotePressed(self, fret: int, string: int):
        self.removeSingleNote((fret, string))

    def initialize(self):
        self.setAttribute(QtCore.Qt.WA_InputMethodEnabled, False)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setCacheMode(QtWidgets.QGraphicsView.CacheBackground)
        self.setViewportUpdateMode(
            QtWidgets.QGraphicsView.MinimalViewportUpdate)
        self.setRenderHints(QtGui.QPainter.Antialiasing |
                            QtGui.QPainter.TextAntialiasing |
                            QtGui.QPainter.SmoothPixmapTransform)
        self.setOptimizationFlag(QtWidgets.QGraphicsView.DontClipPainter, True)
        self.setOptimizationFlag(
            QtWidgets.QGraphicsView.DontSavePainterState, True)
        self.setOptimizationFlag(
            QtWidgets.QGraphicsView.DontAdjustForAntialiasing, True)
        self.setBackgroundBrush(QtWidgets.QApplication.palette().base())

    def initGui(self):
        self.scene().clear()
        # tuning
        self.tuning_items = [
            QGraphicsTextItem(string_name)
            for string_name in self.tuning
        ]
        for i, ti in enumerate(self.tuning_items):
            ti.setFont(QFont("Courier New", 6))
            ti.setPos(
                i * self.FRETWIDTH - ti.boundingRect().width() / 2.,
                0.
            )
            self.scene().addItem(ti)

        self.y_offset = self.tuning_items[0].boundingRect().height()

        # nutmeg
        self.nutmeg_item = QGraphicsLineItem(
            0.,
            self.y_offset,
            (self.num_strings - 1) * self.FRETWIDTH,
            self.y_offset
        )
        self.nutmeg_item.setZValue(1)
        self.nutmeg_item.setPen(QPen(QtCore.Qt.black, 3.))
        self.scene().addItem(self.nutmeg_item)

        # initialize frets and strings
        self.fretboard = FretboardItem(
            self.num_frets,
            self.num_strings,
            self.FRETWIDTH,
            self.FRETHEIGHT,
            QPointF(0, self.y_offset)
        )
        self.fretboard.setPen(QPen(QtCore.Qt.darkGray, 1))
        self.fretboard.open_bottom = self.open_bottom
        self.fretboard.open_top = self.open_top
        self.scene().addItem(self.fretboard)

        # fret label
        self.fret_text_item = QGraphicsTextItem()
        self.fret_text_item.setDefaultTextColor(QtCore.Qt.darkGray)
        fret_pos = QPointF(-20, self.y_offset - 10)
        fret_font = QFont("Courier New", 7, weight=100)
        self.fret_text_item.setPos(fret_pos)
        self.fret_text_item.setFont(fret_font)
        self.scene().addItem(self.fret_text_item)
        # to keep the symmetry
        self.fret_text_dummy_item = QGraphicsTextItem()
        self.fret_text_dummy_item.setVisible(False)
        fret_pos.setX(self.FRETWIDTH * (self.num_strings - 1))
        self.fret_text_dummy_item.setFont(fret_font)
        self.fret_text_dummy_item.setPos(fret_pos)
        self.scene().addItem(self.fret_text_dummy_item)

        # inlays
        self.inlays = [
            FretboardInlayItem(
                0.,
                (fret - 1) * self.FRETHEIGHT + self.y_offset,
                (self.num_strings - 1) * self.FRETWIDTH,
                self.FRETHEIGHT,
                fret
            )
            for fret in range(1, self.num_frets+1)
        ]
        for inlay in self.inlays:
            inlay.setZValue(-1)
            self.scene().addItem(inlay)

        self.updateFretStart()

        # string buttons
        self.string_button_items = [
            StringButtonItem(
                i,
                i * self.FRETWIDTH - self.STRING_BTN_SITZE / 2.,
                self.y_offset + self.FRETHEIGHT *
                self.num_frets + self.STRING_BTN_SITZE / 2. + 5.,
                self.STRING_BTN_SITZE,
                self.STRING_BTN_SITZE
            )
            for i in range(self.num_strings)
        ]
        for str_btn in self.string_button_items:
            self.scene().addItem(str_btn)

        # connect note press signal to slot
        self.scene().barre_pressed.connect(self.onBarrePressed)
        self.scene().existing_note_pressed.connect(self.onExistingNotePressed)
        self.scene().new_note_pressed.connect(self.onNewNotePressed)

    def setCapo(self, fret: int) -> None:
        self.fret_start = fret
        self.updateFretStart()

    def setTuning(self, tuning_array: list[str]) -> None:
        self.tuning = tuning_array
        self.num_strings = len(tuning_array)
        self.clear()

    def clear(self) -> None:
        self.note_items = {}
        self.barre_items = {}
        self.moving_barre_item = None
        self.note_pressed_coord = None
        self.moving_barre_string_coord = None
        self.moving_barre_fret = None
        self.initGui()
        self.updateActiveStringsAndNotes()

    def updateActiveStringsAndNotes(self) -> None:
        active_strings = set()
        active_notes = {}

        for fret, string in self.note_items:
            active_strings.add(string)
            if string not in active_notes:
                active_notes[string] = fret
            elif fret > active_notes[string]:
                active_notes[string] = fret

        for fret, string_coords in self.barre_items.items():
            for left, right in string_coords:
                for string in range(left, right + 1):
                    active_strings.add(string)
                    if string not in active_notes:
                        active_notes[string] = fret
                    elif fret > active_notes[string]:
                        active_notes[string] = fret

        if self.moving_barre_string_coord:
            left, right = sorted(self.moving_barre_string_coord)
            for string in range(left, right + 1):
                active_strings.add(string)
                if string not in active_notes:
                    active_notes[string] = self.moving_barre_fret
                elif self.moving_barre_fret > active_notes[string]:
                    active_notes[string] = self.moving_barre_fret

        active_strings = set(sorted(active_strings))

        if active_notes != self.active:
            self.scene().notes_changed.emit(active_notes)
            self.active = active_notes

        for i, sbi in enumerate(self.string_button_items):
            sbi.is_active = i in active_strings
            sbi.is_root = False

        if len(active_strings) > 0:
            self.string_button_items[list(active_strings)[0]].is_root = True

    def setOpenTop(self, enable: bool) -> None:
        self.open_top = enable
        self.fretboard.open_top = enable

    def setOpenBottom(self, enable: bool) -> None:
        self.open_bottom = enable
        self.fretboard.open_bottom = enable

    def addSingleNote(self, note_coords: tuple[int, int]) -> None:
        # check if it doesn't exist already
        if note_coords not in self.note_items:
            fret, string = note_coords
            if fret > 0:
                # check if it is not already contained in a barre
                if fret in self.barre_items:
                    for sleft, sright in self.barre_items[fret]:
                        if string >= sleft and string <= sright:
                            return
                # create circle for the note and add to dictionary
                x = string * self.FRETWIDTH - self.NOTEDIAMETER / 2
                y = fret * self.FRETHEIGHT - self.FRETHEIGHT / 2 - self.NOTEDIAMETER / 2
                note = FretboardNoteItem(
                    fret,
                    string,
                    x,
                    y + self.y_offset,
                    self.NOTEDIAMETER,
                    self.NOTEDIAMETER
                )
                # overwrites previous note onthe same string, if any
                for f, s in self.note_items:
                    if s == string:
                        self.removeSingleNote((f, string))
                        break
                note.setBrush(QBrush(note.pen().color()))
                self.scene().addItem(note)
                self.note_items[(fret, string)] = note
            else:
                # adds a dummy value to the dict for tracking
                self.note_items[(fret, string)] = None
            self.updateActiveStringsAndNotes()

    def removeSingleNote(self, note_coords: tuple[int, int]) -> None:
        fret, string = note_coords
        if (fret, string) in self.note_items:
            if fret > 0:
                # open strings are not added to the scene
                self.scene().removeItem(self.note_items[(fret, string)])
            del self.note_items[(fret, string)]
            self.updateActiveStringsAndNotes()

    def addBarreItem(self, fret: int, string_coord: tuple[int, int], item: FretboardBarreItem) -> None:
        # make sure the string coordinates are sorted from left to right
        string_coord = tuple(sorted(string_coord))
        if fret not in self.barre_items:
            # first barre in fret, add it
            self.barre_items[fret] = {string_coord: item}
        else:
            # check if there are overlapping barres on the same fret and keep track of
            # them for later deletion
            coords_to_delete = []
            for coord in self.barre_items[fret]:
                # sort the barres string coord tuples so that they ordered from left to right
                coord_pair = sorted(
                    [string_coord, coord])
                # check for overlap or if they are glued to each other
                overlap = coord_pair[1][0] - coord_pair[0][1]
                if overlap <= 1:
                    # no need to max for leftmost with coord_pair[1][0], as it's been sorted above
                    leftmost_string = coord_pair[0][0]
                    rightmost_string = max(
                        coord_pair[1][1], coord_pair[0][1])
                    string_coord = (
                        leftmost_string, rightmost_string)
                    coords_to_delete += [coord]

            # we should add the new "super" barre and delete the overlapped ones
            if len(coords_to_delete) > 0:
                for coord in coords_to_delete:
                    self.removeBarreItem(fret, coord)

                self.scene().removeItem(item)

                (x, y, w, h) = self.calculateBarreRect(fret, string_coord)
                item_to_add = FretboardBarreItem(
                    fret, string_coord, x, y + self.y_offset, w, h
                )
                self.barre_items[fret][string_coord] = item_to_add
                self.scene().addItem(item_to_add)
            else:
                self.barre_items[fret][string_coord] = item
        self.updateActiveStringsAndNotes()

    def removeBarreItem(self, fret: int, string_coords: tuple[int, int]) -> None:
        if fret in self.barre_items and string_coords in self.barre_items[fret]:
            self.scene().removeItem(self.barre_items[fret][string_coords])
            del self.barre_items[fret][string_coords]
            self.updateActiveStringsAndNotes()

    def calculateBarreRect(self, fret: int, string_coords: tuple[int, int]):
        x0, x1 = sorted(string_coords)
        x = x0 * self.FRETWIDTH
        w = (x1 - x0) * self.FRETWIDTH
        y = fret * self.FRETHEIGHT - self.FRETHEIGHT / 2 - self.BARRE_THICKNESS / 2

        return (x, y, w, self.BARRE_THICKNESS)

    def updateFretStart(self) -> None:
        self.setOpenTop(self.fret_start > 0)
        self.fret_text_item.setVisible(self.fret_start > 0)
        self.nutmeg_item.setVisible(self.fret_start == 0)
        fret_digit_last = (self.fret_start % 10)
        fret_digit_before_last = (self.fret_start // 10) % 10

        if fret_digit_before_last == 1:
            superscript = "th"
        else:
            if fret_digit_last == 1:
                superscript = "st"
            elif fret_digit_last == 2:
                superscript = "nd"
            elif fret_digit_last == 3:
                superscript = "rd"
            else:
                superscript = "th"
        html = "{}<sup>{}</sup>".format(self.fret_start, superscript)
        self.fret_text_item.setHtml(html)
        self.fret_text_dummy_item.setHtml(html)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    w = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(w)
    fretboard = FretboardView()
    fretboard.setOpenBottom(True)
    lay.addWidget(fretboard)
    w.resize(480, 640)
    w.show()
    sys.exit(app.exec_())

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsEllipseItem, \
    QGraphicsSceneMouseEvent, QGraphicsTextItem, QGraphicsLineItem, QAbstractGraphicsShapeItem
from PyQt5.QtCore import QRectF, QLineF, QPointF, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPen, QLinearGradient, QColor, QBrush, QTransform, QFont


class FretboardNoteItem(QGraphicsEllipseItem):
    def __init__(self, fret: int, string: int, x: float, y: float, w: float, h: float, parent=None):
        QGraphicsEllipseItem.__init__(self, x, y, w, h, parent)
        self.m_fret = fret
        self.m_string = string

    def mousePressEvent(self, event):
        self.scene().existing_note_pressed.emit(self.m_fret, self.m_string)
        super().mousePressEvent(event)
        event.accept()


class FretboardBarreItem(QGraphicsRectItem):
    CIRCLE_SIZE = 6

    def __init__(self, fret: int, string_coords: tuple[int, int], x: float, y: float, w: float, h: float, parent=None):
        QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        self.string_coords = tuple(sorted(string_coords))
        self.fret = fret

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.scene().barre_pressed.emit(self.fret, self.string_coords)
        super().mousePressEvent(event)
        event.accept()

    def paint(self, painter: QtGui.QPainter, option, widget) -> None:
        painter.setBrush(QtCore.Qt.black)
        painter.setPen(QtCore.Qt.black)
        # main rectangle
        painter.drawRect(self.rect())
        # left ellipse
        bl = self.rect().bottomLeft()
        tl = self.rect().topLeft()
        center = QPointF(bl.x(), (bl.y() + tl.y()) / 2.)
        painter.drawEllipse(center, self.CIRCLE_SIZE /
                            2., self.CIRCLE_SIZE / 2.)
        # right ellipse
        br = self.rect().bottomRight()
        tr = self.rect().topRight()
        center = QPointF(br.x(), (br.y() + tr.y()) / 2.)
        painter.drawEllipse(center, self.CIRCLE_SIZE /
                            2., self.CIRCLE_SIZE / 2.)
        self.scene().update()


class FretboardRectItem(QGraphicsRectItem):
    def __init__(self, fret: int, string: tuple[int, int], rect=QtCore.QRectF(), parent=None):
        QGraphicsRectItem.__init__(self, rect, parent)
        self.m_pressed = False
        self.m_open_top = False
        self.m_open_bottom = False
        self.m_fret = fret
        self.m_string = string

    def paint(self, painter, option, widget):
        if not self.m_open_top and not self.m_open_bottom:
            painter.setPen(self.pen())
            painter.drawRect(self.rect())
        else:
            x1, y1, x2, y2 = self.rect().getCoords()
            initial_color = self.pen().color()
            transparent_pen = QPen(QColor(0, 0, 0, 0))
            initial_pen = QPen(initial_color)
            if self.m_open_top:
                grad_pos_top = 0.0
                grad_pos_bottom = 1.0
                transparent_line = QLineF(x1, y1, x2, y1)
                solid_line = QLineF(x1, y2, x2, y2)
            else:
                grad_pos_top = 1.0
                grad_pos_bottom = 0.0
                transparent_line = QLineF(x1, y2, x2, y2)
                solid_line = QLineF(x1, y1, x2, y1)

            grad_pen_left = QPen(initial_color)
            grad_pen_right = QPen(initial_color)
            grad_left = QLinearGradient(x1, y1, x1, y2)
            grad_left.setColorAt(grad_pos_top, QColor(0, 0, 0, 0))
            grad_left.setColorAt(grad_pos_bottom,  initial_color)
            grad_right = QLinearGradient(grad_left)
            grad_right.setStart(x2, y1)
            grad_right.setFinalStop(x2, y2)
            grad_pen_left.setBrush(QBrush(grad_left))
            grad_pen_right.setBrush(QBrush(grad_right))

            # draw transparent
            painter.setPen(transparent_pen)
            painter.drawLine(transparent_line)
            # draw solid line
            painter.setPen(initial_pen)
            painter.drawLine(solid_line)
            # draw gradient vertical lines
            painter.setPen(grad_pen_left)
            painter.drawLine(QLineF(x1, y1, x1, y2))
            painter.setPen(grad_pen_right)
            painter.drawLine(QLineF(x2, y1, x2, y2))

            # recover original
            painter.setPen(initial_pen)

    def calculateFretString(self, pos):
        x = pos.x()
        left = self.rect().left()
        right = self.rect().right()
        ind = int(round((x - left) / (right - left)))
        string = self.m_string[ind]
        fret = self.m_fret

        return (fret, string)

    def mousePressEvent(self, event):
        self.m_pressed = True
        fret, string = self.calculateFretString(event.pos())
        self.scene().new_note_pressed.emit(fret, string)
        super().mousePressEvent(event)
        event.accept()


class StringButtonItem(QGraphicsRectItem):
    def __init__(self, x: float, y: float, w: float, h: float, parent=None) -> None:
        super().__init__(x, y, w, h, parent)
        self.is_root = False
        self.is_active = False

    def paint(self, painter: QtGui.QPainter, option, widget) -> None:
        painter.setPen(QtCore.Qt.darkGray)
        rect = self.rect()
        if not self.is_active:
            painter.drawLine(QLineF(rect.topLeft(), rect.bottomRight()))
            painter.drawLine(QLineF(rect.bottomLeft(), rect.topRight()))
        else:
            if self.is_root:
                painter.setBrush(QtCore.Qt.darkGray)
            painter.drawEllipse(rect)


class MyGraphicsScene(QGraphicsScene):
    barre_pressed = pyqtSignal(int, tuple)
    existing_note_pressed = pyqtSignal(int, int)
    new_note_pressed = pyqtSignal(int, int)


class FretboardView(QtWidgets.QGraphicsView):
    FRETWIDTH, FRETHEIGHT = 20, 30
    NOTEDIAMETER = 7
    BARRE_THICKNESS = NOTEDIAMETER
    STRING_BTN_SITZE = 5

    def __init__(self, num_frets=6, num_strings=6, fret_start=5, parent=None):
        super().__init__(parent)
        self.initialize()

        self.m_num_frets = num_frets
        self.m_num_strings = num_strings
        self.note_items = {}
        self.barre_items = {}
        self.curr_barre_item = None
        self.note_coord = None
        self.barre_string_coord = None
        self.barre_fret = None

        # set up scene
        scene = MyGraphicsScene(QtCore.QRectF(
            0, 0, self.FRETWIDTH * self.m_num_frets, self.FRETHEIGHT * self.m_num_strings), self)
        self.setScene(scene)

        # initialize frets and strings
        self.fret_rect = [
            [FretboardRectItem(i+1, (j, j+1),
                               QRectF(j * self.FRETWIDTH, i * self.FRETHEIGHT, self.FRETWIDTH, self.FRETHEIGHT))
                for j in range(num_strings-1)
             ] for i in range(num_frets-1)
        ]
        for frets in self.fret_rect:
            for rect in frets:
                rect.setPen(QPen(QtCore.Qt.gray, 1))
                self.scene().addItem(rect)

        # fret label
        self.fret_text_item = QGraphicsTextItem()
        self.fret_text_item.setDefaultTextColor(QtCore.Qt.darkGray)
        self.fret_text_item.setPos(QPointF(-20, 0))
        self.fret_text_item.setFont(QFont("Courier New", 7, weight=100))
        self.scene().addItem(self.fret_text_item)

        # nutmeg
        self.nutmeg_item = QGraphicsLineItem(
            0., 0., (self.m_num_strings - 1) * self.FRETWIDTH, 0.)
        self.nutmeg_item.setPen(QPen(QtCore.Qt.black, 3.))
        self.scene().addItem(self.nutmeg_item)

        self.setFretStart(fret_start)

        # string buttons
        self.string_button_items = [
            StringButtonItem(i * self.FRETWIDTH - self.STRING_BTN_SITZE / 2.,
                             self.FRETHEIGHT *
                             (self.m_num_frets - 1) +
                             self.STRING_BTN_SITZE / 2. + 5.,
                             self.STRING_BTN_SITZE,
                             self.STRING_BTN_SITZE)
            for i in range(self.m_num_strings)
        ]
        for str_btn in self.string_button_items:
            self.scene().addItem(str_btn)

        # connect note press signal to slot
        self.scene().barre_pressed.connect(self.onBarrePressed)
        self.scene().existing_note_pressed.connect(self.onExistingNotePressed)
        self.scene().new_note_pressed.connect(self.onNewNotePressed)

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
        sp = self.mapToScene(event.pos())
        item = self.scene().itemAt(sp, QTransform())
        if item and (isinstance(item, FretboardRectItem) or isinstance(item, FretboardBarreItem)):
            fret = 1 + int(sp.y() / self.FRETHEIGHT)
            string = int((sp.x() + self.FRETWIDTH / 2) / self.FRETWIDTH)

            if (fret, string) == self.note_coord:
                # the barre is reduced to a single note: delete the current barre if any
                # and generate a note
                if self.curr_barre_item:
                    self.scene().removeItem(self.curr_barre_item)
                    self.curr_barre_item = None
                    self.barre_string_coord = None
                    self.barre_fret = None
                self.addSingleNote((fret, string))
            elif self.note_coord:
                # We're in barre mode: check if we need to create one,  extend it or shrink it
                # Extension or reduction only happens if the string index is different than
                # the last barre string.
                if self.barre_string_coord is None or string != self.barre_string_coord[1]:
                    self.barre_fret = self.note_coord[0]
                    self.barre_string_coord = (
                        self.note_coord[1], string)

                    # we delete the old barre before generating the new one
                    if self.curr_barre_item:
                        self.scene().removeItem(self.curr_barre_item)

                    # check if the barre intersects with any notes and overwrite them (delete the notes)
                    coords_to_delete = []
                    leftmost_string, rightmost_string = sorted(
                        self.barre_string_coord)
                    for note_fret, note_string in self.note_items:
                        if note_fret == self.barre_fret and \
                                note_string >= leftmost_string and \
                                note_string <= rightmost_string:
                            coords_to_delete += [(note_fret, note_string)]

                    for coord in coords_to_delete:
                        self.removeSingleNote(coord)

                    (x, y, w, h) = self.calculateBarreRect(
                        fret, self.barre_string_coord)

                    self.curr_barre_item = FretboardBarreItem(
                        self.barre_fret, self.barre_string_coord, x, y, w, h
                    )

                    self.scene().addItem(self.curr_barre_item)

        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.curr_barre_item and self.barre_string_coord and self.barre_fret:
            self.addBarreItem(
                self.barre_fret, self.barre_string_coord, self.curr_barre_item)

        self.barre_fret = None
        self.barre_string_coord = None
        self.curr_barre_item = None
        self.note_coord = None

        return super().mouseReleaseEvent(event)

    @pyqtSlot(int, int)
    def onNewNotePressed(self, fret: int, string: int):
        self.note_coord = (fret, string)
        self.addSingleNote(self.note_coord)

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

    def setOpenTop(self, enable: bool):
        for rect in self.fret_rect[0]:
            rect.m_open_top = enable

    def setOpenBottom(self, enable: bool):
        for rect in self.fret_rect[-1]:
            rect.m_open_bottom = enable

    def addSingleNote(self, note_coords: tuple[int, int]):
        if note_coords not in self.note_items:
            fret, string = note_coords
            # create circle for the note and add to dictionary
            x = string * self.FRETWIDTH - self.NOTEDIAMETER / 2
            y = fret * self.FRETHEIGHT - self.FRETHEIGHT / 2 - self.NOTEDIAMETER / 2
            note = FretboardNoteItem(
                fret, string, x, y, self.NOTEDIAMETER, self.NOTEDIAMETER)
            note.setBrush(QBrush(note.pen().color()))
            self.scene().addItem(note)
            self.note_items[(fret, string)] = note

    def removeSingleNote(self, note_coords: tuple[int, int]):
        fret, string = note_coords
        if (fret, string) in self.note_items:
            self.scene().removeItem(self.note_items[(fret, string)])
            del self.note_items[(fret, string)]

    def addBarreItem(self, fret: int, string_coord: tuple[int, int], item: FretboardBarreItem):
        # make sure the string coordinates are sorted from left to right
        string_coord = tuple(sorted(string_coord))
        if fret not in self.barre_items:
            # first barre in fret, add it
            self.barre_items[fret] = {
                string_coord: item}
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

            # we should add the overlapped barre if we deleted the overlapped ones
            if len(coords_to_delete) > 0:
                for coord in coords_to_delete:
                    self.removeBarreItem(fret, coord)

                self.scene().removeItem(item)

                (x, y, w, h) = self.calculateBarreRect(fret, string_coord)
                item_to_add = FretboardBarreItem(
                    fret, string_coord, x, y, w, h
                )
                self.barre_items[fret][string_coord] = item_to_add
                self.scene().addItem(item_to_add)
            else:
                self.barre_items[fret][string_coord] = item

    def removeBarreItem(self, fret: int, string_coords: tuple[int, int]):
        if fret in self.barre_items and string_coords in self.barre_items[fret]:
            self.scene().removeItem(self.barre_items[fret][string_coords])
            del self.barre_items[fret][string_coords]

    def calculateBarreRect(self, fret: int, string_coords: tuple[int, int]):
        x0, x1 = string_coords
        if x1 >= x0:
            # positive barre (from cursor original initial click, dragging to the right)
            x = x0 * self.FRETWIDTH - self.BARRE_THICKNESS / 2
            w = (x1 - x0) * self.FRETWIDTH + self.BARRE_THICKNESS
        else:
            # negative barre (from cursor original initial click, dragging to the left)
            x = x1 * self.FRETWIDTH - self.BARRE_THICKNESS / 2
            w = (x0 - x1) * self.FRETWIDTH + self.BARRE_THICKNESS

        y = fret * self.FRETHEIGHT - \
            self.FRETHEIGHT / 2 - self.BARRE_THICKNESS / 2

        return (x, y, w, self.BARRE_THICKNESS)

    def setFretStart(self, fret: int):
        self.setOpenTop(fret > 0)
        self.fret_text_item.setVisible(fret > 0)
        self.nutmeg_item.setVisible(fret == 0)
        fret_digit_last = (fret % 10)
        fret_digit_before_last = (fret // 10) % 10

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
        # self.fret_start = fret
        self.fret_text_item.setHtml(
            "{}<sup>{}</sup>".format(fret, superscript))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('fusion')
    w = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(w)
    lay.addWidget(QtWidgets.QLabel("Fretboard",
                  alignment=QtCore.Qt.AlignCenter))
    fretboard = FretboardView()
    fretboard.setOpenBottom(True)
    lay.addWidget(fretboard)
    w.resize(640, 480)
    w.show()
    sys.exit(app.exec_())

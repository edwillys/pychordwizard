from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsSceneMouseEvent
from PyQt5.QtCore import QLineF, QPointF, QRectF, QSizeF
from PyQt5.QtGui import QPen, QLinearGradient, QColor, QBrush, QPainter


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

    def shape(self) -> QtGui.QPainterPath:
        path = super().shape()
        # TODO: why doesn't this work?
        cl, cr = self.getRoundingEllipseCenters()
        path.addEllipse(cl, self.CIRCLE_SIZE / 2., self.CIRCLE_SIZE / 2.)
        path.addEllipse(cr, self.CIRCLE_SIZE / 2., self.CIRCLE_SIZE / 2.)
        path.setFillRule(QtCore.Qt.WindingFill)
        return path

    def paint(self, painter: QtGui.QPainter, option, widget) -> None:
        painter.setBrush(QtCore.Qt.black)
        painter.setPen(QtCore.Qt.black)
        # main rectangle
        painter.drawRect(self.rect())
        # left and right rounding corner ellipsi
        cl, cr = self.getRoundingEllipseCenters()
        painter.drawEllipse(cl, self.CIRCLE_SIZE / 2., self.CIRCLE_SIZE / 2.)
        painter.drawEllipse(cr, self.CIRCLE_SIZE / 2., self.CIRCLE_SIZE / 2.)
        self.scene().update()

    def getRoundingEllipseCenters(self):
        rect = self.rect()
        bl = rect.bottomLeft()
        tl = rect.topLeft()
        br = rect.bottomRight()
        tr = rect.topRight()
        cl = QPointF(bl.x(), (bl.y() + tl.y()) / 2.)
        cr = QPointF(br.x(), (br.y() + tr.y()) / 2.)
        return (cl, cr)


class FretboardItem(QGraphicsRectItem):
    def __init__(self, num_frets: int, num_strings: int, fret_w: int, fret_h: int,
                 topLeft: QPointF):
        rect = QRectF(topLeft, QSizeF(
            num_strings * fret_w, num_frets * fret_h))
        QGraphicsRectItem.__init__(self, rect)
        self.open_top = False
        self.open_bottom = False
        self.num_frets = num_frets
        self.num_strings = num_strings
        self.fret_w = fret_w
        self.fret_h = fret_h
        self.topLeft = topLeft

    def paintFretboard(self, painter: QPainter, fret_start: int, fret_end: int):
        fret_diff = fret_end - fret_start
        start_point = QPointF(
            self.topLeft.x(), self.topLeft.y() + fret_start * self.fret_h)
        rect = QRectF(start_point, QSizeF(
            (self.num_strings - 1) * self.fret_w, fret_diff * self.fret_h))
        painter.drawRect(rect)
        y0 = self.topLeft.y() + fret_start * self.fret_h
        y1 = y0 + fret_diff * self.fret_h
        for string in range(1, self.num_strings - 1):
            x0 = string * self.fret_w
            x1 = x0
            painter.drawLine(QLineF(x0, y0, x1, y1))
        
        x0 = self.topLeft.x()
        x1 = x0 + self.fret_w * (self.num_strings - 1)
        for fret in range(fret_start, fret_end):
            y0 = self.topLeft.y() + fret * self.fret_h
            y1 = y0
            painter.drawLine(QLineF(x0, y0, x1, y1))

    def paintGradientStrings(self, painter: QPainter, fret_start: int, fret_end: int, is_top: bool):
        # x1, y1, x2, y2 = self.rect().getCoords()
        initial_color = self.pen().color()
        transparent_pen = QPen(QColor(0, 0, 0, 0))
        initial_pen = QPen(initial_color)
        if is_top:
            grad_pos_top = 0.0
            grad_pos_bottom = 1.0
        else:
            grad_pos_top = 1.0
            grad_pos_bottom = 0.0

        y0 = self.topLeft.y() + fret_start * self.fret_h
        y1 = self.topLeft.y() + fret_end * self.fret_h
        for string in range(self.num_strings):
            x0 = string * self.fret_w
            x1 = x0
            grad_pen = QPen(initial_color)
            grad = QLinearGradient(x0, y0, x1, y1)
            grad.setColorAt(grad_pos_top, QColor(0, 0, 0, 0))
            grad.setColorAt(grad_pos_bottom,  initial_color)
            grad_pen.setBrush(QBrush(grad))
            painter.setPen(grad_pen)
            painter.drawLine(QLineF(x0, y0, x1, y1))

        # recover original
        painter.setPen(initial_pen)

    def paint(self, painter: QPainter, option, widget):
        painter.setPen(self.pen())
        if not self.open_top and not self.open_bottom:
            self.paintFretboard(painter, 0, self.num_frets)
        elif self.open_top and self.open_bottom:
            self.paintFretboard(painter, 1, self.num_frets - 1)
            self.paintGradientStrings(painter, 0, 1, True)
            self.paintGradientStrings(
                painter, self.num_frets - 1, self.num_frets, False)
        elif self.open_top:
            self.paintGradientStrings(painter, 0, 1, True)
            self.paintFretboard(painter, 1, self.num_frets)
        else:
            self.paintFretboard(painter, 0, self.num_frets - 1)
            self.paintGradientStrings(
                painter, self.num_frets - 1, self.num_frets, False)

    def calculateFretString(self, pos):
        x = pos.x()
        y = pos.y()
        left = self.rect().left()
        right = self.rect().right()
        top = self.rect().top()
        bottom = self.rect().bottom()
        ind_x = (x - left) / (right - left)
        ind_y = (y - top) / (bottom - top)
        fret = 1 + int((ind_y * self.num_frets))
        string = int(round(ind_x * self.num_strings))

        return (fret, string)

    def mousePressEvent(self, event):
        fret, string = self.calculateFretString(event.pos())
        self.scene().new_note_pressed.emit(fret, string)
        super().mousePressEvent(event)
        event.accept()

class StringButtonItem(QGraphicsRectItem):
    def __init__(self, string: int, x: float, y: float, w: float, h: float, parent=None) -> None:
        super().__init__(x, y, w, h, parent)
        self.is_root = False
        self.is_active = False
        self.string = string

    def paint(self, painter: QtGui.QPainter, option, widget) -> None:
        painter.setPen(QtCore.Qt.darkGray)
        rect = self.rect()
        if not self.is_active:
            painter.drawLine(QLineF(rect.topLeft(), rect.bottomRight()))
            painter.drawLine(QLineF(rect.bottomLeft(), rect.topRight()))
        else:
            if self.is_root:
                painter.setBrush(QtCore.Qt.darkGray)
            else:
                painter.setBrush(QBrush())
            painter.drawEllipse(rect)
        self.scene().update()

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        if self.is_active:
            self.scene().existing_note_pressed.emit(0, self.string)
        else:
            self.scene().new_note_pressed.emit(0, self.string)
        event.accept()
        return super().mousePressEvent(event)


class FretboardInlayItem(QGraphicsRectItem):
    def __init__(self, x: float, y: float, w: float, h: float,
                 fret: int, num_strings: int, size: int = 5, 
                 style: str = "dot", parent=None) -> None:
        QGraphicsRectItem.__init__(self, x, y, w, h, parent)
        self.size = size
        self.fret = fret
        self.style = style
        self.num_strings = num_strings

    def paint(self, painter: QtGui.QPainter, option, widget) -> None:
        norm_fret = self.fret % 13
        rect = self.rect()
        center = rect.center()
        cx = center.x()
        x_offset = rect.width() / (self.num_strings - 1.)

        if self.style == "dot":
            color = QColor(QtCore.Qt.lightGray)
            color.setAlphaF(0.5)
            painter.setBrush(color)
            pen = QPen(QtCore.Qt.gray)
            pen.setWidthF(1.)
            painter.setPen(pen)
            if norm_fret == 3 or norm_fret == 5 or \
                    norm_fret == 7 or norm_fret == 9:
                if self.num_strings % 2:
                    cl = QPointF(cx - (0.5 * x_offset), center.y())
                    cr = QPointF(cx + (0.5 * x_offset), center.y())
                    painter.drawEllipse(cl, self.size / 2., self.size / 2.)
                    painter.drawEllipse(cr, self.size / 2., self.size / 2.)
                else:
                    painter.drawEllipse(center, self.size / 2., self.size / 2.)
            elif norm_fret == 12:
                if self.num_strings % 2:
                    cl = QPointF(cx - (1.5 * x_offset), center.y())
                    cr = QPointF(cx + (1.5 * x_offset), center.y())
                else:
                    cl = QPointF(cx - x_offset, center.y())
                    cr = QPointF(cx + x_offset, center.y())
                painter.drawEllipse(cl, self.size / 2., self.size / 2.)
                painter.drawEllipse(cr, self.size / 2., self.size / 2.)
        self.scene().update()

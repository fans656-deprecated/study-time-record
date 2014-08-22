import sys

from PySide.QtGui import *
from PySide.QtCore import *

import util
import config
import record

@util._super
class Widget(QDialog):

    def __init__(self, parent=None):
        self._super().__init__(parent)
        # data
        self.started = False
        self.records = record.Records(config.RECORD_FILENAME)
        self.spans = self.records.lastRecord().spans()
        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimeout)
        # misc
        self.setTitle()
        self.resize(*config.WINDOW_SIZE)
        self.timer.start(config.REFRESH_INTERVAL)

    def onTimeout(self):
        self.records.update()
        if self.needRedraw():
            self.update()

    def needRedraw(self):
        spans = self.records.lastRecord().spans()
        if self.spans == spans:
            return False
        else:
            self.spans = spans
            return True

    def keyPressEvent(self, event):
        if not event.isAutoRepeat():
            if event.text() == ' ':
                self.toggle()
                return
            elif event.text() == 's':
                self.records.printDailyAverage()
                return
            # this showed that text drawing is time consuming
            elif event.text() == 'm':
                if self.width() > 400:
                    self.resize(320, 240)
                else:
                    self.hide()
                    self.showMaximized()
                return
        self._super().keyPressEvent(event)

    def paintEvent(self, event):
        p = QPainter(self)
        # misc
        rc = self.rect()
        textHeight = rc.height() / 3
        # font
        font = p.font()
        font.setFamily('Inconsolata')
        font.setPixelSize(textHeight)
        p.setFont(font)
        # data
        spans = self.spans
        colors = ('#D5D5D5', '#BDF2BC', '#FACA8E')
        # paint
        p.fillRect(rc, QBrush(QColor('#000')))
        for span, color in zip(spans, colors):
            pen = p.pen()
            pen.setColor(QColor(color))
            p.setPen(pen)
            p.drawText(rc, Qt.AlignRight, span)
            rc.translate(0, textHeight)

    def toggle(self):
        self.records.toggle()
        self.started = not self.started
        self.setTitle()

    def setTitle(self):
        self.setWindowTitle('Running' if self.started else 'Stopped')

    def done(self, result):
        if self.started:
            self.toggle()
        else:
            self.records.save()
        super(Widget, self).done(result)

app = QApplication(sys.argv)
w = Widget()
w.showMaximized()
app.exec_()

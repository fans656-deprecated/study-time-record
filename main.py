import sys

from PySide.QtGui import *
from PySide.QtCore import *

import record

RECORD_FILENAME = 'studyTimeRecord.txt'

class Widget(QDialog):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        # data
        self.started = False
        self.records = record.Records(RECORD_FILENAME)
        self.spans = []
        # timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.onTimeout)
        # misc
        self.setTitle()
        self.resize(320, 240)
        # go
        self.timer.start(100)

    def onTimeout(self):
        self.records.update()
        spans = [getattr(self.records.lastRecord(), _)() for _ in
                ['currentSessionSpan', 'todayTotalSpan', 'todayLeftSpan']]
        # text drawing is time consuming
        # so only if the updated spans is different from the previous ones
        # then we actually do the drawing
        if self.spans != spans:
            #print self.spans, spans
            self.spans = spans
            self.update()

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
        super(Widget, self).keyPressEvent(event)

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

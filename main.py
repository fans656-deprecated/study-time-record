import sys
import datetime

from PySide.QtGui import *
from PySide.QtCore import *

@util._super
class Widget(QDialog):

    def __init__(self, parent=None):
        self._super().__init__(parent)
        # data
        self.started = False
        self.isDrawingStatistics = False
        self.statisticsHeight = 0.0
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
                self.isDrawingStatistics = not self.isDrawingStatistics 
                if self.isDrawingStatistics:
                    self.records.printDailyAverage()
                    self.averageSeconds = self.records.averageSeconds()
                    self.statisticsHeight = self.height() * config.statisticsHeightRatio
                    self.update()
                else:
                    self.statisticsHeight = 0.0
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
        p.fillRect(self.rect(), QColor('#000'))

        self.drawRecord(p)
        if self.isDrawingStatistics:
            self.drawRecordsStat(p)

    def drawRecord(self, painter):
        rc = self.rect()
        rc.setBottom(rc.bottom() - self.statisticsHeight)
        textHeight = rc.height() / 3

        font = painter.font()
        font.setFamily('Inconsolata')
        font.setPixelSize(textHeight)
        painter.setFont(font)

        spans = self.spans
        colors = ('#D5D5D5', '#BDF2BC', '#FACA8E')

        for span, color in zip(spans, colors):
            pen = painter.pen()
            pen.setColor(QColor(color))
            painter.setPen(pen)
            painter.drawText(rc, Qt.AlignRight, span)
            rc.translate(0, textHeight)

    def drawRecordsStat(self, painter):
        records = self.records.records
        dx = self.width() / float(len(records))
        # hue saturation value
        hueLow = config.hueLow
        hueHigh = config.hueHigh
        hueRange = hueHigh - hueLow
        # histogram
        expectSeconds = config.EXPECT_SPAN.total_seconds()
        color = QColor()
        for i, record in enumerate(records):
            ratio = record.totalSeconds() / expectSeconds
            h = self.statisticsHeight * ratio
            rc = QRect(i * dx, self.height() - h, dx - 1, h)
            color.setHsv(hueLow + hueRange * ratio, config.saturation, config.value)
            painter.fillRect(rc, color)
        # separation line
        pen = painter.pen(); pen.setColor(QColor(*config.separationLineColor)); painter.setPen(pen)
        y = self.height() - self.statisticsHeight
        painter.drawLine(0, y, self.width(), y)
        # average line
        pen = painter.pen(); pen.setColor(QColor(*config.averageLineColor)); painter.setPen(pen)
        y = self.height() - self.statisticsHeight * self.averageSeconds / expectSeconds
        painter.drawLine(0, y, self.width(), y)

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

import sys

from PySide.QtCore import *
from PySide.QtGui import *

import qt
import util
import config

@util._super
class Widget(QDialog):
    def __init__(self, records, parent=None):
        self._super().__init__(parent)

        self.records = records
        self.timer = qt.timer(self, 100, self.onTimeout)

        self.showMaximized()

    def onTimeout(self):
        self.update()

    def paintEvent(self, event):
        marginRatio = float(config.get('margin-ratio'))
        margin = self.rect().width() * marginRatio

        rcRecord = self.rect()
        rcRecord.adjust(0, 0, -margin, 0)

        painter = QPainter(self)

        self.drawBackground(painter)
        self.drawLastRecord(painter, rcRecord, self.records.lastRecord())

    def drawBackground(self, painter):
        painter.fillRect(self.rect(), config.get('color-back'))

    def drawLastRecord(self, painter, rc, record):
        textHeight = rc.height() / 3.0
        rcText = QRect(rc)
        rcText.setBottom(rcText.top() + textHeight)

        spans = record.formatedSpans()
        colors = (QColor(config.get('color-' + name)) for name in
                ('session', 'total', 'remain'))

        qt.font(painter,
                family=config.get('font'),
                pixel=textHeight * float(config.get('font-shrink-ratio')))
        for span, color in zip(spans, colors):
            qt.pen(painter, color=color)
            painter.drawText(rcText, Qt.AlignCenter | Qt.AlignRight, span)
            rcText.translate(0, textHeight)

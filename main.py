import sys
import datetime
import time
import itertools
import re
from PySide.QtGui import *
from PySide.QtCore import *

RECORD_FILENAME = 'studyTimeRecord.txt'
EXPECT_SPAN = datetime.timedelta(hours=8)
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT = '{} {}'.format(DATE_FORMAT, TIME_FORMAT)

now = lambda: datetime.datetime.now()
fmtTime = lambda t: t.strftime(TIME_FORMAT)
fmtDate = lambda t: t.strftime(DATE_FORMAT)
fmtDateTime = lambda t: t.strftime(DATETIME_FORMAT)
fmtSpan = lambda t: re.match('.*(\d+:\d{2}:\d{2}).*', str(t)).group(1)
pDate = lambda s: datetime.datetime.strptime(s, DATE_FORMAT)
pTime = lambda s: datetime.datetime.strptime(s, TIME_FORMAT)

class Session:
    def __init__(self, *args):
        self.started = False
        if not args:
            t = now()
            self.init(t, t)
        elif len(args) == 1:
            sBegEnd = args[0]
            self.init(*(pTime(_) for _ in sBegEnd.split()))

    def init(self, beg, end):
        self.beg, self.end = beg, end

    def start(self):
        self.beg = now()
        self.started = True

    def stop(self):
        self.end = now()
        self.started = False

    def update(self):
        if self.started:
            self.end = now()
            self.valid = True

    def span(self):
        return datetime.timedelta(seconds=(self.end - self.beg).seconds)

    def __repr__(self):
        return '{} {}'.format(*(fmtTime(_) for _ in (self.beg, self.end)))

class Record:
    def __init__(self, date=None, *sessions):
        self.date = date if date else fmtDate(now())
        self.sessions = [Session(_) for _ in sessions] + [Session()]
        self.nOldSessions = len(self.sessions) - 1
        self.update()

    def start(self):
        self.lastSession().start()

    def stop(self):
        self.lastSession().stop()
        self.sessions.append(Session())

    def update(self):
        self.lastSession().update()
        self.total = sum((_.span() for _ in self.sessions), datetime.timedelta())

    def currentSessionSpan(self):
        return fmtSpan(self.lastSession().span())

    def todayTotalSpan(self):
        return fmtSpan(self.total)

    def todayLeftSpan(self):
        text = fmtSpan(abs(EXPECT_SPAN - self.total))
        if EXPECT_SPAN < self.total:
            text = '-' + text
        return text

    def lastSession(self):
        return self.sessions[-1]

    def __repr__(self):
        return '{}\n{}'.format(self.date, '\n'.join(map(str, self.sessions)))

    def save(self, isNew):
        with open(RECORD_FILENAME, 'a') as f:
            if isNew:
                f.write('\n\n{}'.format(self.date))
            for session in self.sessions[self.nOldSessions:-1]:
                f.write('\n{}'.format(session))
            self.nOldSessions = len(self.sessions) - 1

class Records:
    def __init__(self, fileName=None):
        if fileName:
            self.load(fileName)
        self.started = False

    def toggle(self):
        if not self.started:
            self.start()
        else:
            self.stop()

    def start(self):
        self.lastRecord().start()
        self.started = True

    def stop(self):
        self.lastRecord().stop()
        self.save()
        self.started = False

    def update(self):
        self.lastRecord().update()

    def load(self, fileName):
        lines = [_.strip() for _ in open(fileName).readlines()]
        self.records = [Record(*g) for k, g in itertools.groupby(lines, bool) if k]
        # today record
        try:
            lastRec = self.records[-1]
        except IndexError:
            lastRec = None
        rec = Record()
        self.isNewRecord = not lastRec or lastRec.date != rec.date
        if self.isNewRecord:
            self.records.append(rec)

    def save(self):
        self.lastRecord().save(self.isNewRecord)
        self.isNewRecord = False

    def lastRecord(self):
        return self.records[-1]

    def printDailyAverage(self):
        nDays = (now() - pDate(self.records[0].date)).days + 1
        ave = sum((_.total / nDays for _ in self.records), datetime.timedelta())
        print '{} in {} days'.format(ave, nDays)

class Widget(QDialog):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        # data
        self.started = False
        self.records = Records(RECORD_FILENAME)
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

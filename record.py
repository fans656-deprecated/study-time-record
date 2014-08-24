import itertools
import re
import datetime
import time
import collections

import config

EXPECT_SPAN = config.EXPECT_SPAN
DATE_FORMAT = config.DATE_FORMAT
TIME_FORMAT = config.TIME_FORMAT
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
            # zero spaned session, beg == end
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
        # if no record data (i.e. sessions) available
        # then make sure there are at least one (zero spaned) session
        self.sessions = map(Session, sessions) + [Session()]
        self.nOldSessions = len(sessions)
        self.update()

    def getDate(self):
        dt = datetime.datetime.strptime(self.date, config.DATE_FORMAT)
        return dt.date()

    def start(self):
        self.lastSession().start()

    def stop(self):
        self.lastSession().stop()
        self.sessions.append(Session())

    def update(self):
        self.lastSession().update()
        self.total = sum((_.span() for _ in self.sessions), datetime.timedelta())

    def spans(self):
        getters = (getattr(self, attrName) for attrName in
                 ('currentSessionSpan', 'todayTotalSpan', 'todayLeftSpan'))
        spans = (getter() for getter in getters)
        return [fmtSpan(span) for span in spans]

    def totalSeconds(self):
        return self.total.total_seconds()

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
        with open(config.RECORD_FILENAME, 'a') as f:
            if isNew:
                # write date
                f.write('\n{}\n'.format(self.date))
            # Though seems like we are not saving the last session
            # into file, we won't lose anything.
            # Because when we save, we will always at a stoped stage.
            # And Record.stop() will stop the running session and
            # append a new one.
            # So we only lose the new appended zero spaned session
            # which is indeed not for saving into file.
            for session in self.sessions[self.nOldSessions:-1]:
                # write session
                f.write('{}\n'.format(session))
            # now we only have one unsaved (zero spaned) session
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
        lines = [_.strip() for _ in open(config.RECORD_FILENAME).readlines()]
        self.records = [Record(*g) for k, g in itertools.groupby(lines, bool) if k]
        todayRecord = Record()
        if self.records:
            self.isNewRecord = self.lastRecord().date != todayRecord.date
        else:
            self.isNewRecord = True
        if self.isNewRecord:
            self.records.append(todayRecord)
        self.insertMissedRecords()

    def insertMissedRecords(self):
        try:
            firstRecord = self.records[0]
            lastRecord = self.records[-1]
        except IndexError:
            return
        beg = firstRecord.getDate()
        end = lastRecord.getDate()
        nDays = (end - beg).days + 1

        availRecords = collections.deque(self.records)
        records = []
        dates = (beg + datetime.timedelta(days=i) for i in range(nDays))
        for date in dates:
            availRecord = availRecords[0]
            if date == availRecord.getDate():
                record = availRecord
                availRecords.popleft()
            else:
                record = Record(fmtDate(date))
            records.append(record)
        self.records = records

    def save(self):
        self.lastRecord().save(self.isNewRecord)
        self.isNewRecord = False

    def lastRecord(self):
        return self.records[-1]

    def averageSeconds(self):
        nDays = (now() - pDate(self.records[0].date)).days + 1
        ave = sum((_.total / nDays for _ in self.records), datetime.timedelta())
        return ave.total_seconds()

if __name__ == '__main__':
    records = Records(config.RECORD_FILENAME)

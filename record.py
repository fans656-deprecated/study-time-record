class Record:
    def formatedSpans(self):
        return ('hello', 'world', 'this')

class Records:
    def __init__(self, filename):
        self.filename = filename

    def lastRecord(self):
        return Record()

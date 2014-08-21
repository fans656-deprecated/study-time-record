import qt
import config
from widget import Widget
from record import Records

config.clear()
config.setDefault({
    'record-file': 'studyTimeRecord.txt',
    'color-session': '#D5D5D5',
    'color-total': '#BDF2BC',
    'color-remain': '#FACA8E',
    'color-back': '#000000',
    'font': 'Inconsolata',
    'font-shrink-ratio': '0.6',
    'margin-ratio': '0.05',
    })

records = Records(config.get('record-file'))
wiget = Widget(records)
qt.run()
config.save()

import datetime

RECORD_FILENAME = 'studyTimeRecord.txt'
EXPECT_SPAN = datetime.timedelta(hours=8)

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

WINDOW_SIZE = (320, 240)
REFRESH_INTERVAL = 100

hueLow = 0
hueHigh = 145
saturation = 255 * 0.54
value = 255 * 0.8

separationLineColor = (255, 255, 255)
averageLineColor = (38, 133, 50)
statisticsHeightRatio = 0.3

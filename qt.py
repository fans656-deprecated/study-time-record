import sys

from PySide.QtCore import *
from PySide.QtGui import *


app = QApplication(sys.argv)

def run():
    app.exec_()

def font(painter, **attrs):
    _setAttrs(painter, 'font', attrs, {
        'family': 'setFamily',
        'pixel': 'setPixelSize',
        })

def pen(painter, **attrs):
    _setAttrs(painter, 'pen', attrs, {
        'color': 'setColor',
        })

def timer(obj, interval, callback):
    t = QTimer()
    t.timeout.connect(callback)
    t.start(interval)
    return t

def _setAttrs(painter, objname, attrs, attrSetters):
    objGetter = getattr(painter, objname)
    obj = objGetter()
    for name, value in attrs.items():
        setter = getattr(obj, attrSetters[name])
        setter(value)
    objSetter = getattr(painter, 'set' + objname.capitalize())
    objSetter(obj)

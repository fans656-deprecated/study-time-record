import ConfigParser

_filename = 'config.txt'
_config = ConfigParser.ConfigParser()

def setFilename(filename):
    global _filename
    _filename = filename

def clear():
    open(_filename, 'w')

def setDefault(default):
    global _config
    _config = ConfigParser.ConfigParser(default)
    _config.read(_filename)

def get(key):
    return _config.get('DEFAULT', key)

def save():
    with open(_filename, 'w') as f:
        _config.write(f)

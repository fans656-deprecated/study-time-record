def _super(cls):
    setattr(cls, '_super', lambda self: super(cls, self))
    return cls

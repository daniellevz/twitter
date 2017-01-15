class Context(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        self.pop(key)
    
    def update(self, kwds):
        for key, value in kwds.items():
            self[key] = value

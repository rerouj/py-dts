from threading import Lock


class CacheMeta(type):

    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(CacheMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def get(self, key):
        ...
    def set(self, key, value):
        ...
    def delete(self, key):
        ...
    def clear(self):
        ...
    def cache_size(self):
        ...

class Cache(metaclass=CacheMeta):

    _instance = None

    def __init__(self):
        print("Cache initialized")
        if not hasattr(self, 'initialized'):
            self.cache = {}
            self.cache_size = 0
            self.cache_limit = 1000

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        if self.cache_size >= self.cache_limit:
            self.clear()
        self.cache[key] = value
        self.cache_size += 1

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]
            self.cache_size -= 1

    def clear(self):
        self.cache.clear()
        self.cache_size = 0
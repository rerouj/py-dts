class BadRangeError(Exception):
    def __init__(self, msg):
        self.msg = msg

class CollectionNotFoundError(Exception):
    """
    Exception raised when a collection is not found in the index or in the metadata file.
    """
    def __init__(self, msg):
        self.msg = msg

class ResourceNotFoundError(Exception):
    """
    Exception raised when a resource (document) is not found.
    """
    def __init__(self, msg):
        self.msg = msg

class MediaTypeError(Exception):
    """
    Exception raised when a media type is not supported.
    """
    def __init__(self, msg):
        self.msg = msg

class NetworkError(ConnectionError):
    """
    Exception related with network connection problems
    """
    def __init__(self, msg):
        self.msg = msg
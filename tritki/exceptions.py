class TritkiError(Exception):
    pass

class UIError(ImportError, TritkiError):
    pass

class FileLoadError(FileNotFoundError, TritkiError):
    pass
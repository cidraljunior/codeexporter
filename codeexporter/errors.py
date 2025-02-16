class ExportError(Exception):
    """Base exception for code export operations."""


class UnreadableFileError(ExportError):
    """Raised when a file cannot be read."""

    def __init__(self, path, reason):
        super().__init__(f"Cannot read file {path}: {reason}")


class InvalidConfigError(ExportError):
    """Raised for configuration errors."""

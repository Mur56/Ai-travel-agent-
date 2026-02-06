class CustomException(Exception):
    """Base class for custom exceptions in the project."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"CustomException: {self.message}" 
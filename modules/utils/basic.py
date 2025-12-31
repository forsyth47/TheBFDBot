import os

class BasicUtils:
    @staticmethod
    def ensure_directory_exists(directory_path: str):
        """Ensure that a directory exists; if not, create it."""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

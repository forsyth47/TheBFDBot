class DownloadCancelled(Exception):
    def __init__(self, action):
        self.action = action

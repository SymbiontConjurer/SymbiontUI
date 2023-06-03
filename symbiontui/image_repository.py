import os
import imghdr

class ImageRepository:
    def __init__(self, directory):
        self.directory = directory

    def list(self):
        files_and_dirs = os.listdir(self.directory)
        images = sorted(
            [f for f in files_and_dirs if os.path.isfile(os.path.join(self.directory, f)) and imghdr.what(os.path.join(self.directory, f))],
            key=lambda x: os.stat(os.path.join(self.directory, x)).st_ctime,
            reverse=True  # Descending order
        )
        return images

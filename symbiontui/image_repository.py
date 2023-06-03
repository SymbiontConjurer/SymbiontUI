from dataclasses import dataclass
from typing import List, Set
import os
import imghdr

@dataclass
class Image:
    name: str
    relpath: str
    abspath: str
    tags: List[str]
    category: str

class ImageRepository:
    def __init__(self, directory: str):
        self.directory = directory
        self.images = self._load_images()

    def _get_image_category(self, image_path: str) -> List[str]:
        filename = os.path.basename(image_path)
        if 'grid' in filename:
            return ['grid']
        return ['image']

    def _load_images(self) -> List[Image]:
        files_and_dirs = os.listdir(self.directory)
        images = sorted(
            [
                Image(
                    os.path.splitext(f)[0],
                    os.path.join(f), # Relative path
                    os.path.join(self.directory, f),  # Absolute path
                    [],
                    self._get_image_category(os.path.join(self.directory, f))
                )
                for f in files_and_dirs
                if os.path.isfile(os.path.join(self.directory, f)) and imghdr.what(os.path.join(self.directory, f))
            ],
            key=lambda x: os.stat(x.abspath).st_ctime,
            reverse=True  # Descending order
        )
        return images

    def list(self, category: str = None) -> List[Image]:
        if not category:
            return self.images
        return [image for image in self.images if category in image.category]

    def categories(self) -> Set[str]:
        return {"image", "grid"}

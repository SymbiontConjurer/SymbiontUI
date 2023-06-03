from dataclasses import dataclass
from typing import List
import os
import imghdr

@dataclass
class ImageData:
    name: str
    path: str
    tags: List[str]
    category: str

class ImageRepository:
    def __init__(self, directory):
        self.directory = directory

    def _get_image_category(self, image_path: str) -> List[str]:
        filename = os.path.basename(image_path)
        if 'grid' in filename:
            return ['grid']
        return ['image']

    def list(self, category: str = None) -> List[ImageData]:
        files_and_dirs = os.listdir(self.directory)
        images = sorted(
            [ImageData(f, os.path.join(self.directory, f), [], self._get_image_category(os.path.join(self.directory, f))) 
            for f in files_and_dirs 
            if os.path.isfile(os.path.join(self.directory, f)) and imghdr.what(os.path.join(self.directory, f))],
            key=lambda x: os.stat(x.path).st_ctime,
            reverse=True  # Descending order
        )
        
        if category:
            images = [image for image in images if category in image.category]
            
        return images

    def categories(self) -> set:
        return {"image", "grid"}

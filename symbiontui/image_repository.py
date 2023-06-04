from dataclasses import dataclass
from typing import List, Optional, Set
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
        images = []
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if os.path.isfile(os.path.join(root, file)) and imghdr.what(os.path.join(root, file)):
                    rel_path = os.path.join(os.path.relpath(root, self.directory), file)
                    images.append(
                        Image(
                            os.path.splitext(file)[0],
                            rel_path,
                            os.path.join(root, file),
                            [],
                            self._get_image_category(os.path.join(root, file))
                        )
                    )
        # Sort the images
        images.sort(key=lambda x: os.stat(x.abspath).st_ctime, reverse=True)
        return images

    def list(self, category: Optional[str] = None) -> List[Image]:
        if not category:
            return self.images
        return [image for image in self.images if category in image.category]

    def categories(self) -> Set[str]:
        return {"image", "grid"}

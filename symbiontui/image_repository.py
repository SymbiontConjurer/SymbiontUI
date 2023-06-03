import os
import imghdr
from dataclasses import dataclass
from typing import List, Optional, Set


@dataclass
class ImageData:
    name: str
    path: str
    tags: List[str]
    category: str


class ImageRepository:
    def __init__(self, directory):
        self.directory = directory

    def list(self, category: Optional[str] = None):
        files_and_dirs = os.listdir(self.directory)
        images = sorted(
            [
                ImageData(
                    name=f,
                    path=os.path.join(self.directory, f),
                    tags=[],
                    category="image",
                )
                for f in files_and_dirs
                if os.path.isfile(os.path.join(self.directory, f))
                and imghdr.what(os.path.join(self.directory, f))
                and (category is None or category == "image")
            ],
            key=lambda x: os.stat(x.path).st_ctime,
            reverse=True  # Descending order
        )
        return images

    def categories(self) -> Set[str]:
        return {"images"}

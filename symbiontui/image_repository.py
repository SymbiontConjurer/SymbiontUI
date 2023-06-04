from dataclasses import dataclass
from typing import Dict, List, Optional, Set
import os
import imghdr
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@dataclass
class Image:
    name: str
    relpath: str
    abspath: str
    tags: List[str]
    category: str

class ImageChangeHandler(FileSystemEventHandler):
    def __init__(self, repository):
        self.repository = repository

    def on_created(self, event):
        if not event.is_directory and imghdr.what(event.src_path):
            self.repository.add_image(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.repository.remove_image(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and imghdr.what(event.src_path):
            self.repository.update_image(event.src_path)

class ImageRepository:
    def __init__(self, directory: str):
        self.directory = directory
        self.images: Dict[str, Image] = {}
        self._load_images()
        self.observer = Observer()
        self.observer.schedule(ImageChangeHandler(self), self.directory, recursive=True)
        self.observer.start()

    def _get_image_category(self, image_path: str) -> List[str]:
        filename = os.path.basename(image_path)
        if 'grid' in filename:
            return ['grid']
        return ['image']

    def _load_images(self):
        for root, dirs, files in os.walk(self.directory):
            for file in files:
                if os.path.isfile(os.path.join(root, file)) and imghdr.what(os.path.join(root, file)):
                    self.add_image(os.path.join(root, file))

    def add_image(self, image_path: str):
        rel_path = os.path.join(os.path.relpath(os.path.dirname(image_path), self.directory), os.path.basename(image_path))
        self.images[rel_path] = Image(
            os.path.splitext(os.path.basename(image_path))[0],
            rel_path,
            image_path,
            [],
            self._get_image_category(image_path)
        )

    def remove_image(self, image_path: str):
        rel_path = os.path.join(os.path.relpath(os.path.dirname(image_path), self.directory), os.path.basename(image_path))
        if rel_path in self.images:
            del self.images[rel_path]

    def update_image(self, image_path: str):
        self.remove_image(image_path)
        self.add_image(image_path)

    def list(self, category: Optional[str] = None) -> List[Image]:
        if not category:
            return list(self.images.values())
        return [image for image in self.images.values() if category in image.category]

    def categories(self) -> Set[str]:
        return {"image", "grid"}

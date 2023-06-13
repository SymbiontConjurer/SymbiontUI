from dataclasses import dataclass
import logging
from typing import Dict, List, Optional, Set
import os
import imghdr
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

@dataclass
class Image:
    name: str
    relpath: str
    abspath: str
    tags: List[str]
    category: str
    created: datetime
    last_modified: datetime

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'tif']

class ImageChangeHandler(FileSystemEventHandler):
    def __init__(self, repository):
        self.repository = repository

    def _is_image(self, event):
        # verify the event is not for a directory,
        # that the file has an image extension (to avoid tmp files),
        # and that the file is actually an image
        return (not event.is_directory and
            os.path.splitext(event.src_path)[1][1:] in IMAGE_EXTENSIONS)

    def on_created(self, event):
        try:
            if self._is_image(event):
                self.repository.add_image(event.src_path)
        except Exception as e:
            logging.exception("Error adding image to repository", exc_info=True)

    def on_deleted(self, event):
        if self._is_image(event):
            self.repository.remove_image(event.src_path)

    def on_modified(self, event):
        try:
            if self._is_image(event):
                self.repository.update_image(event.src_path)
        except Exception as e:
            logging.exception("Error updating image in repository", exc_info=True)

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
        stat = os.stat(image_path)
        created = datetime.fromtimestamp(stat.st_ctime)
        last_modified = datetime.fromtimestamp(stat.st_mtime)
        rel_path = os.path.join(os.path.relpath(os.path.dirname(image_path), self.directory), os.path.basename(image_path))
        self.images[rel_path] = Image(
            os.path.splitext(os.path.basename(image_path))[0],
            rel_path,
            image_path,
            [],
            self._get_image_category(image_path),
            created,
            last_modified
        )

    def remove_image(self, image_path: str):
        rel_path = os.path.join(os.path.relpath(os.path.dirname(image_path), self.directory), os.path.basename(image_path))
        if rel_path in self.images:
            del self.images[rel_path]

    def update_image(self, image_path: str):
        self.remove_image(image_path)
        self.add_image(image_path)

    def list(self, category: Optional[str] = None) -> List[Image]:
        images = list(self.images.values())
        if category:
            images = [image for image in images if category in image.category]
        return sorted(images, key=lambda image: image.last_modified, reverse=True)

    def categories(self) -> Set[str]:
        return {"image", "grid"}

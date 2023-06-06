import os
import dataclasses
from datetime import datetime
from pathlib import Path

@dataclasses.dataclass
class Model:
    name: str
    file_type: str
    relpath: str
    abspath: str
    model_type: str
    created: datetime
    last_modified: datetime

def is_automatic1111_path(path: str):
    p = Path(path).resolve()
    return p.is_dir() and p.name.startswith('stable-diffusion-webui')

class Automatic1111(object):
    def __init__(self, base_path):
        base_path = Path(base_path)
        if not is_automatic1111_path(base_path):
            raise ValueError('Path is not a valid automatic1111 repo path.')
        self.base_path = base_path

    @property
    def image_output_path(self):
        return self.base_path / 'outputs'

    @property
    def models_path(self):
        return self.base_path / 'models'

    @property
    def checkpoints_path(self):
        return self.base_path / 'models' / 'Stable-diffusion'

    @property
    def loras_path(self):
        return self.base_path / 'models' / 'Lora'

    @property
    def embeddings_path(self):
        return self.base_path / 'embeddings'

    @property
    def vae_path(self):
        return self.base_path / 'models' / 'VAE'
    
    def get_models(self):
        models_path = Path(self.models_path)
        model_dict = {}
        for subdir in models_path.iterdir():
            if subdir.is_dir():
                model_files = [f for f in subdir.iterdir() if f.is_file()]
                model_objects = []
                for file_path in model_files:
                    model_created = datetime.fromtimestamp(file_path.stat().st_ctime)
                    model_last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)
                    rel_path = Path('models') / subdir.name / file_path.name
                    model_objects.append(Model(name=file_path.name, 
                                               file_type=file_path.suffix,
                                               relpath=str(rel_path), 
                                               abspath=str(file_path.resolve()), 
                                               model_type=subdir.name.lower(),  
                                               created=model_created, 
                                               last_modified=model_last_modified))
                model_dict[subdir.name.lower()] = model_objects
        return model_dict

import os

def is_automatic1111_path(path: str):
    abspath = os.path.abspath(path)
    return os.path.isdir(abspath) and os.path.basename(abspath).startswith('stable-diffusion-webui')

class Automatic1111(object):
    def __init__(self, base_path):
        if not is_automatic1111_path(base_path):
            raise ValueError('Path is not a valid automatic1111 repo path.')
        self.base_path = base_path

    @property
    def image_output_path(self):
        return os.path.join(self.base_path, 'outputs')

    @property
    def models_path(self):
        return os.path.join(self.base_path, 'models')

    @property
    def checkpoints_path(self):
        return os.path.join(self.base_path, 'models/Stable-diffusion')

    @property
    def loras_path(self):
        return os.path.join(self.base_path, 'models/Lora')

    @property
    def embeddings_path(self):
        return os.path.join(self.base_path, 'embeddings')

    @property
    def vae_path(self):
        return os.path.join(self.base_path, 'models/VAE')
    
    def get_models(self):
        models_path = self.models_path
        model_dict = {}
        for subdir in os.listdir(models_path):
            if os.path.isdir(os.path.join(models_path, subdir)):
                model_files = os.listdir(os.path.join(models_path, subdir))
                model_dict[subdir.lower()] = [os.path.join('models', subdir, fname) for fname in model_files]
        return model_dict

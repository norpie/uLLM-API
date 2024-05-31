import os
from pathlib import Path


class DataDir:
    def __init__(self, data_dir):
        if data_dir.startswith("$"):
            data_dir = os.path.expandvars(data_dir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.data_dir = data_dir

    def get_root(self):
        return self.data_dir

    def get_model_path(self):
        if not os.path.exists(os.path.join(self.data_dir, "models")):
            os.makedirs(os.path.join(self.data_dir, "models"))
        return Path(os.path.join(self.data_dir, "models"))

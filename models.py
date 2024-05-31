class ModelManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def list_models(self):
        model_path = self.data_dir.get_model_path()
        return [f.name for f in model_path.iterdir() if f.is_dir()]

class ModelManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.engine = None

    def load_model(self, engine, model_name):
        if model_name not in self.list_models():
            raise ValueError(f"Model {model_name} not found")

        engine = self.get_engine(engine, self.data_dir.get_model_path() / model_name)
        engine.load_model()

    def list_models(self):
        model_path = self.data_dir.get_model_path()
        return [f.name for f in model_path.iterdir() if f.is_dir()]

    def current_engine(self):
        return self.engine

    def get_engine(self, engine, path):
        if engine == "exllamav2":
            return Testengine(path)
        else:
            raise ValueError(f"Unknown engine: {engine}")


class Testengine:
    def __init__(self, path):
        self.path = path

    def load_model(self):
        return True

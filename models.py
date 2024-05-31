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
            return Engine(path)
        else:
            raise ValueError(f"Unknown engine: {engine}")


class Engine:
    def __init__(self, path):
        self.path = path
        self.parameters = None

    def set_parameters(self, parameters):
        self.parameters = parameters

    def reload_model(self):
        self.unload_model()
        self.load_model()

    def load_model(self):
        raise NotImplementedError

    def unload_model(self):
        raise NotImplementedError

    def complete(self, prompt):
        raise NotImplementedError

    def complete_streaming(self, prompt, streaming_callback):
        raise NotImplementedError

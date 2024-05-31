class ModelManager:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def list_models(self):
        print("Listing models in {}".format(self.data_dir.get_model_dir()))
        return self.data_dir.get_model_dir()

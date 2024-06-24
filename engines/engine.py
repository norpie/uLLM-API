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

    async def complete(self, prompt):
        return await self.complete_streaming(prompt, None)

    async def complete_streaming(self, prompt, streaming_callback):
        raise NotImplementedError

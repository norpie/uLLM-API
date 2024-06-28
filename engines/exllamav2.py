from engines.engine import Engine
from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Tokenizer,
)

from exllamav2.generator import ExLlamaV2StreamingGenerator, ExLlamaV2Sampler


class ExLlamaV2Engine(Engine):
    def __init__(self, path):
        self.path = path
        self.parameters = None

    def load_model(self):
        self.config = ExLlamaV2Config(str(self.path))
        self.model = ExLlamaV2(self.config)
        self.cache = ExLlamaV2Cache(self.model, max_seq_len=8192, lazy=True)
        self.model.load_autosplit(self.cache)

        self.tokenizer = ExLlamaV2Tokenizer(self.config)
        self.generator = ExLlamaV2StreamingGenerator(
            model=self.model, cache=self.cache, tokenizer=self.tokenizer
        )
        self.generator.set_stop_conditions(
            [self.tokenizer.eos_token_id, 128001, 128002]
        )
        self.settings = ExLlamaV2Sampler.Settings()
        self.settings.temperature = 0.7
        self.settings.top_k = 50
        self.settings.top_p = 0.8

    def unload_model(self):
        if self.model is None:
            return
        self.model.unload()
        self.model = None
        self.cache = None
        self.tokenizer = None
        self.generator = None
        self.settings = None

    async def complete_streaming(self, prompt, streaming_callback):
        if self.generator is None or self.settings is None or self.tokenizer is None:
            return "No model loaded"

        input_ids = self.tokenizer.encode(prompt, add_bos=True)
        if isinstance(input_ids, tuple):
            raise ValueError("Can't handle multiple input_ids")
        self.generator.begin_stream_ex(input_ids, self.settings)

        completion = ""
        generated = 0
        while True:
            res = self.generator.stream_ex()
            chunk, eos = res["chunk"], res["eos"]

            completion += chunk
            generated += 1

            if streaming_callback:
                await streaming_callback(chunk)

            if eos or generated > 256:
                break
        return completion

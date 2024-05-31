from models import Engine
from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Tokenizer,
)

from exllamav2.generator import ExLlamaV2BaseGenerator, ExLlamaV2Sampler


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
        self.generator = ExLlamaV2BaseGenerator(
            model=self.model, cache=self.cache, tokenizer=self.tokenizer
        )
        self.settings = ExLlamaV2Sampler.Settings()
        self.settings.temperature = 0.7
        self.settings.top_k = 50
        self.settings.top_p = 0.8
        self.settings.token_repetition_penalty = 1.01
        self.settings.disallow_tokens(self.tokenizer, [self.tokenizer.eos_token_id])
        self.max_new_tokens = 256
        self.generator.warmup()

    def unload_model(self):
        pass

    def complete(self, prompt):
        completion = self.generator.generate_simple(
            prompt, self.settings, self.max_new_tokens, add_bos=True
        )
        return completion

    def complete_streaming(self, prompt, streaming_callback):
        pass

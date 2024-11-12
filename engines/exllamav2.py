import time
from typing import Awaitable, Callable
from engines.engine import Engine, EngineParameters
from exllamav2 import (
    ExLlamaV2,
    ExLlamaV2Config,
    ExLlamaV2Cache,
    ExLlamaV2Tokenizer,
)

from exllamav2.generator import ExLlamaV2StreamingGenerator, ExLlamaV2Sampler


class ExLlamaV2Engine(Engine):
    def __init__(self, path: str):
        self.path = path

    def load_model(self) -> None:
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
        self.apply_parameters(EngineParameters())

    def unload_model(self) -> None:
        if self.model is None:
            return
        self.model.unload()
        self.model = None
        self.cache = None
        self.tokenizer = None
        self.generator = None
        self.settings = None

    def apply_parameters(self, parameters: EngineParameters) -> None:
        if self.settings is None or self.tokenizer is None:
            raise RuntimeError("No model loaded")

        self.settings.token_repetition_penalty = parameters.repetition_penalty
        self.settings.token_repetition_range = parameters.repetition_penalty_range

        self.settings.temperature = parameters.temperature
        self.settings.smoothing_factor = parameters.smoothing_factor

        self.settings.top_k = parameters.top_k
        self.settings.top_p = parameters.top_p
        self.settings.top_a = parameters.top_a
        self.settings.min_p = parameters.min_p
        self.settings.tfs = parameters.tfs

        self.settings.mirostat = parameters.mirostat
        self.settings.mirostat_tau = parameters.mirostat_tau
        self.settings.mirostat_eta = parameters.mirostat_eta

        self.settings.disallow_tokens(self.tokenizer, parameters.banned_tokens)

    def cancel_streaming(self) -> None:
        self.streaming = False

    async def complete_streaming(
        self,
        parameters: EngineParameters,
        prompt: str,
        stream: Callable[[str], Awaitable[None]] | None,
    ) -> str:
        if self.generator is None or self.settings is None or self.tokenizer is None:
            raise RuntimeError("No model loaded")

        self.apply_parameters(parameters)

        input_ids = self.tokenizer.encode(prompt, add_bos=True)
        if isinstance(input_ids, tuple):
            raise ValueError("Can't handle multiple input_ids")
        self.streaming = True
        self.generator.begin_stream_ex(input_ids, self.settings)

        completion = ""
        stop_reason = ""
        time_start = time.time()
        while True:
            res = self.generator.stream_ex()
            chunk, eos = res["chunk"], res["eos"]

            completion += chunk

            if stream:
                await stream(chunk)

            if eos:
                stop_reason = "EOS"
                break
            if len(completion) >= parameters.max_tokens:
                stop_reason = "max_tokens"
                break
            ends, seq = parameters.ends_with_stop_sequence(chunk)
            if ends:
                stop_reason = f"stop_sequences ({seq})"
                break
            if not self.streaming:
                stop_reason = "cancelled"
                break
        time_end = time.time()
        print(
            f"Generated {len(completion)} tokens in {time_end - time_start:.2f}s at a rate of {len(completion) / (time_end - time_start):.2f} tokens/s, generation stopped because of {stop_reason}"
        )
        return completion

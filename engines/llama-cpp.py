import time
from typing import Awaitable, Callable

from engines.engine import Engine, EngineParameters
from llama_cpp import Llama


class LlamaCppEngine(Engine):
    def __init__(self, path: str):
        self.path = path

    def load_model(self) -> None:
        self.llama = Llama(self.path, n_ctx=4096)

    def unload_model(self) -> None:
        if self.llama:
            del self.llama
        pass

    def apply_parameters(self, parameters: EngineParameters) -> None:
        self.llama.settings()
        pass

    def cancel_streaming(self) -> None:
        self.streaming = False

    async def complete_streaming(
        self,
        parameters: EngineParameters,
        prompt: str,
        stream: Callable[[str], Awaitable[None]] | None,
    ) -> str:
        completion = ""
        stop_reason = ""
        time_start = time.time()
        generator = self.llama.generate(
            self.llama.tokenize(prompt.encode()),
            top_k=parameters.top_k,
            top_p=parameters.top_p,
            min_p=parameters.min_p,
            typical_p=parameters.typical_p,
            temp=parameters.temperature,
            repeat_penalty=parameters.repetition_penalty,
            frequency_penalty=parameters.frequency_penalty,
            presence_penalty=parameters.presence_penalty,
            tfs_z=parameters.tfs,
            mirostat_mode=parameters.mirostat_mode,
            mirostat_eta=parameters.mirostat_eta,
            mirostat_tau=parameters.mirostat_tau,
        )
        for token in generator:
            detokenized = self.llama.detokenize([token])

            chunk = detokenized.decode()
            completion += chunk

            if stream:
                await stream(chunk)

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
        if stop_reason == "":
            stop_reason = "EOS"
        time_end = time.time()
        print(
            f"Generated {len(completion)} tokens in {time_end - time_start:.2f}s at a rate of {len(completion) / (time_end - time_start):.2f} tokens/s, generation stopped because of {stop_reason}"
        )
        return completion

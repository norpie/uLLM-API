from enum import Enum
import json
import asyncio
from typing import Awaitable, Callable, List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class EngineParameters:
    max_tokens: Optional[int] = 512
    context_window: Optional[int] = 4096

    temperature: Optional[float] = 0.5
    top_k: Optional[int] = 50
    top_p: Optional[float] = 0.8

    typical_p: Optional[float] = 1.0
    min_p: Optional[float] = 0.1
    top_a: Optional[float] = 0.0

    tfs: Optional[float] = 1.0
    epsilon_cutoff: Optional[float] = 0.0
    eta_cutoff: Optional[float] = 0.0

    repetition_penalty: Optional[float] = 1.05
    repetition_penalty_range: Optional[int] = 1024
    encoder_penalty: Optional[float] = 1.0

    frequency_penalty: Optional[float] = 1.05
    presence_penalty: Optional[float] = 0.0
    no_repeat_ngram_size: Optional[float] = 0.0

    smoothing_factor: Optional[float] = 0.33
    smoothing_curve: Optional[float] = 1.0

    # DRY Repetition Penalty
    dry_muiltiplier: Optional[float] = 0.8
    dry_base: Optional[float] = 1.75
    dry_allowed_length: Optional[int] = 2
    dry_sequence_breakers: Optional[List[str]] = field(
        default_factory=lambda: ["\n", ":", '"', "*"]
    )

    # Dynamic Temperature
    dt: Optional[bool] = False
    dt_min_temperature: Optional[float] = 0
    dt_max_temperature: Optional[float] = 2

    # Mirostat
    mirostat: Optional[bool] = False
    mirostat_mode: Optional[int] = 0
    mirostat_tau: Optional[float] = 5.0
    mirostat_eta: Optional[float] = 0.1

    # Beam Search
    bs: Optional[bool] = False
    bs_n: Optional[int] = 1
    bs_lenth_penalty: Optional[float] = 0.0
    bs_early_stopping: Optional[bool] = False

    # Contrastive Search
    cs: Optional[bool] = False
    cs_penalty_alpha: Optional[float] = 0.0

    # Sampling
    do_sample: Optional[bool] = True
    add_beos_token: Optional[bool] = True
    ban_beos_token: Optional[bool] = False
    skip_special_tokens: Optional[bool] = False
    temperature_last: Optional[bool] = True

    banned_tokens: Optional[List[int]] = field(default_factory=list)
    banned_strings: Optional[List[str]] = field(default_factory=list)

    stop_sequences: Optional[List[str]] = field(default_factory=list)

    def ends_with_stop_sequence(self, completion: str) -> Tuple[bool, str]:
        if not self.stop_sequences:
            return False, ""
        for stop_sequence in self.stop_sequences:
            if stop_sequence in completion:
                return True, stop_sequence
        return False, ""

    @staticmethod
    def from_json(json_string: str) -> "EngineParameters":
        data = json.loads(json_string)
        return EngineParameters(**data)

    @staticmethod
    def from_dict(data: dict) -> "EngineParameters":
        return EngineParameters(**{**EngineParameters().__dict__, **data})


class Engine:
    def __init__(self, path: str):
        self.path = path

    def reload_model(self) -> None:
        self.unload_model()
        self.load_model()

    def load_model(self) -> None:
        raise NotImplementedError

    def unload_model(self) -> None:
        raise NotImplementedError

    def apply_parameters(self, parameters: EngineParameters) -> None:
        raise NotImplementedError

    def complete(self, parameters: EngineParameters, prompt: str) -> str:
        # run the async function in the event loop
        return asyncio.run(self.complete_streaming(parameters, prompt, None))

    def cancel_streaming(self) -> None:
        raise NotImplementedError

    async def complete_streaming(
        self,
        parameters: EngineParameters,
        prompt: str,
        stream: Callable[[str], Awaitable[None]] | None,
    ) -> str:
        raise NotImplementedError


class EngineType(Enum):
    EXLLAMAV2 = "exllamav2"
    LLAMA_CPP = "llama-cpp"
    TRANSFORMERS = "transformers"

    @staticmethod
    def from_str(s: str) -> "EngineType":
        for engine in EngineType:
            if engine.value == s:
                print(f"Determine engine type: {engine} for {s}")
                return engine
        raise ValueError(f"Unknown engine type: {s}")

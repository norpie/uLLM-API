from enum import Enum
from typing import Awaitable, Callable, List, Tuple


class EngineParameters:
    def __init__(self):
        self.max_tokens = 512
        self.context_window = 4096

        self.temperature = 0.5
        self.top_k = 50
        self.top_p = 0.8

        self.typical_p = 1.0
        self.min_p = 0.1
        self.top_a = 0.0

        self.tfs = 1.0
        self.epsilon_cutoff = 0.0
        self.eta_cutoff = 0.0

        self.repetition_penalty = 1.05
        self.repetition_penalty_range = 1024
        self.encoder_penalty = 1.0

        self.frequency_penalty = 1.05
        self.presence_penalty = 0.0
        self.no_repeat_ngram_size = 0.0

        self.smoothing_factor = 0.33
        self.smoothing_curve = 1.0

        # DRY Repetition Penalty
        self.dry_muiltiplier = 0.8
        self.dry_base = 1.75
        self.dry_allowed_length = 2
        self.dry_sequence_breakers = ["\n", ":", "\"", "*"]

        # Dynamic Temperature
        self.dt = False
        self.dt_min_temperature = 0
        self.dt_max_temperature = 2
        self.dt_exponent = 1

        # Mirostat
        self.mirostat = False
        self.mirostat_mode = 0 # 0: off, 1: ?, 2: ?
        self.mirostat_tau = 5.0
        self.mirostat_eta = 0.1

        # Beam Search
        self.bs = False
        self.bs_n = 1
        self.bs_lenth_penalty = 0.0
        self.bs_early_stopping = False

        # Contrastive Search
        self.cs = False
        self.cs_penalty_alpha = 0.0

        # Sampling
        self.do_sample = True
        self.add_beos_token = True
        self.ban_beos_token = False
        self.skip_special_tokens = False
        self.temperature_last = True

        self.banned_tokens: List[int] = []
        self.banned_strings: List[str] = []

        self.stop_sequences: List[str] = []

    def ends_with_stop_sequence(self, completion: str) -> Tuple[bool, str]:
        for stop_sequence in self.stop_sequences:
            if completion.endswith(stop_sequence):
                return True, stop_sequence
        return False, ""


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

    async def complete(self, parameters: EngineParameters, prompt: str) -> str:
        return await self.complete_streaming(parameters, prompt, None)

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

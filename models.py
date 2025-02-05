from dataclasses import dataclass
from enum import Enum
import time
import json

from exllamav2.generator.base import threading
from engines.engine import Engine, EngineType
from engines.exllamav2 import ExLlamaV2Engine
# from engines.llama_cpp import LlamaCppEngine
from data import DataDir


class ModelStatus(Enum):
    NO_MODEL = "no_model"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"


@dataclass()
class SimpleModel:
    engine: str
    model: str

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class ModelManager:
    def __init__(self, data_dir: DataDir):
        self.data_dir = data_dir
        self.engine = None
        self.engine_type = None
        self.status = ModelStatus.NO_MODEL
        self.model_name = None
        self.timeout_sec = 900
        self.running = False
        self.timer_thread = None
        self.used = time.time()

    def load_model(
        self, engine: EngineType, model_name: str, timeout_sec: int = 900000
    ) -> None:
        self.timeout_sec = timeout_sec
        self.used = time.time()
        list = self.list_models()
        if not any(d["name"] == model_name for d in list):
            raise ValueError(f"Model {model_name} not found")
        if self.engine is not None:
            self.engine.unload_model()
        try:
            self.status = ModelStatus.LOADING
            self.engine_type = engine
            self.engine = self.get_engine(
                engine, self.data_dir.get_model_path() / model_name
            )
            self.engine.load_model()
            self.status = ModelStatus.LOADED
            self.model_name = model_name
            self.start_timer()
        except Exception as e:
            self.status = ModelStatus.ERROR
            self.engine = None
            self.model_name = None
            raise e

    def unload_model(self) -> None:
        print("Unloading model")
        if self.timer_thread is not None:
            self.running = False
            self.timer_thread = None
        if self.engine is not None:
            self.engine.unload_model()
            del self.engine
            self.engine = None
            self.status = ModelStatus.UNLOADED

    def model_status(self) -> dict[str, str | None]:
        status = self.status.value
        engine_type = self.engine_type.value if self.engine_type is not None else None
        return {"status": status, "engine": engine_type, "model": self.model_name}

    def list_models(self) -> list[dict[str, str]]:
        model_path = self.data_dir.get_model_path()
        return [{"engine": "llama-cpp", "name": f.name} for f in model_path.iterdir()]

    def start_timer(self):
        if not self.running:
            self.running = True
            self.used = time.time()
            self.timer_thread = threading.Thread(target=self.check_timeout)
            self.timer_thread.start()

    def check_timeout(self):
        while self.running:
            time.sleep(1)  # sleep for 1 second
            since_used = time.time() - self.used
            if since_used > self.timeout_sec:
                print("Timeout reached, unloading model")
                self.used = time.time()
                self.unload_model()
                break

    def current_engine(self) -> Engine | None:
        self.used = time.time()
        return self.engine

    def get_engine(self, engine: EngineType, path) -> Engine:
        print(f"Loading model {engine} from {path}")
        if engine == EngineType.EXLLAMAV2:
            return ExLlamaV2Engine(path)
        # if engine == EngineType.LLAMA_CPP:
            # return LlamaCppEngine(path)
        else:
            raise NotImplementedError(f"Engine {engine} not implemented")

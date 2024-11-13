from enum import Enum
import time
import os

from exllamav2.generator.base import threading
from engines.engine import Engine, EngineType
from engines.exllamav2 import ExLlamaV2Engine
from engines.llama_cpp import LlamaCppEngine
from data import DataDir


class ModelStatus(Enum):
    NO_MODEL = "No model loaded"
    LOADING = "loading"
    LOADED = "loaded"
    UNLOADED = "unloaded"
    ERROR = "error"


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
        self, engine: EngineType, model_name: str, timeout_sec: int = 900
    ) -> None:
        self.timeout_sec = timeout_sec
        list = self.list_models()
        if model_name not in list:
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
        if self.timer_thread is not None:
            self.running = False
            self.timer_thread = None
        if self.engine is not None:
            self.engine.unload_model()
            self.engine = None
            self.status = ModelStatus.UNLOADED

    def model_status(self) -> tuple[ModelStatus, EngineType | None, str | None]:
        return self.status, self.engine_type, self.model_name

    def list_models(self) -> list[str]:
        model_path = self.data_dir.get_model_path()
        return [f.name for f in model_path.iterdir()]

    def start_timer(self):
        if not self.running:
            self.running = True
            self.timer_thread = threading.Thread(target=self.check_timeout)
            self.timer_thread.start()

    def check_timeout(self):
        while self.running:
            time.sleep(1)  # sleep for 1 second
            since_used = time.time() - self.used
            if since_used > self.timeout_sec:
                print("Timeout reached, unloading model")
                self.used = False
                self.unload_model()
                break

    def current_engine(self) -> Engine | None:
        # Start timeout timer
        self.used = time.time()
        if (
            self.status == ModelStatus.UNLOADED
            and self.model_name is not None
            and self.engine_type is not None
        ):
            self.load_model(self.engine_type, self.model_name)
        return self.engine

    def get_engine(self, engine: EngineType, path) -> Engine:
        if engine == EngineType.EXLLAMAV2:
            return ExLlamaV2Engine(path)
        if engine == EngineType.LLAMA_CPP:
            return LlamaCppEngine(path)
        else:
            raise NotImplementedError(f"Engine {engine} not implemented")

import json
from fastapi import FastAPI
from pydantic import BaseModel
from models import ModelManager
from embed import EmbedManager
from engines.engine import EngineType, EngineParameters
import uvicorn


class TextRequest(BaseModel):
    text: str


def start(host: str,
          port: int,
          model_manager: ModelManager,
          embed_manager: EmbedManager):
    import threading

    thread = threading.Thread(target=run, args=(host, port, model_manager, embed_manager))
    thread.start()


def run(host: str, port: int, model_manager: ModelManager, embed_manager: EmbedManager):
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ping": "pong"}

    @app.get("/models")
    def list_models():
        return model_manager.list_models()

    @app.post("/models/{engine}/{model_name}")
    def load_model(engine: str, model_name: str):
        try:
            engine_type = EngineType[engine]
            model_manager.load_model(engine_type, model_name)
            return model_manager.model_status()
        except ValueError as e:
            return {"error": str(e)}

    @app.get("/status")
    def status():
        return model_manager.model_status()

    @app.post("/embed")
    def embed(req: TextRequest):
        return { "embeddings": embed_manager.embed(req.text) }

    @app.delete("/models")
    def unload_model():
        model_manager.unload_model()
        return model_manager.model_status()

    @app.post("/complete")
    def complete(req: TextRequest):
        engine = model_manager.current_engine()
        if engine is None:
            return {"error": "No model loaded"}
        parameters = EngineParameters()
        return {"completion": engine.complete(parameters, req.text)}

    uvicorn.run(app, host=host, port=port)

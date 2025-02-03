from fastapi import FastAPI
from pydantic import BaseModel
from models import ModelManager
from engines.engine import EngineType, EngineParameters
import uvicorn


class CompletionRequest(BaseModel):
    text: str


def start(host: str, port: int, model_manager: ModelManager):
    import threading

    thread = threading.Thread(target=run, args=(host, port, model_manager))
    thread.start()


def run(host: str, port: int, model_manager: ModelManager):
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
            return {"status": model_manager.model_status()}
        except ValueError as e:
            return {"error": str(e)}

    @app.delete("/models")
    def unload_model():
        model_manager.unload_model()
        return {"status": model_manager.model_status()}

    @app.post("/complete")
    def complete(req: CompletionRequest):
        engine = model_manager.current_engine()
        if engine is None:
            return {"error": "No model loaded"}
        parameters = EngineParameters()
        return {"completion": engine.complete(parameters, req.text)}

    uvicorn.run(app, host=host, port=port)

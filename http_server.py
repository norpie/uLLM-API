from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


class CompletionRequest(BaseModel):
    text: str

def start(host, port, model_manager):
    import threading
    thread = threading.Thread(target=run, args=(host, port, model_manager))
    thread.start()


def run(host, port, model_manager):
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
            model_manager.load_model(engine, model_name)
            return {"status": "loading"}
        except ValueError as e:
            return {"error": str(e)}

    @app.delete("/models")
    def unload_model():
        engine = model_manager.current_engine()
        if engine is None:
            return {"error": "No model loaded"}
        engine.unload_model()
        return {"status": "unloaded"}

    @app.get("/complete")
    def complete(req: CompletionRequest):
        engine = model_manager.current_engine()
        if engine is None:
            return {"error": "No model loaded"}
        return {"completion": engine.complete(req.text)}

    uvicorn.run(app, host=host, port=port)

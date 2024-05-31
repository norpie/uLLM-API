from fastapi import FastAPI
import uvicorn

def run(host, port, model_manager):
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return "pong"

    @app.get("/models")
    def list_models():
        return model_manager.list_models()

    uvicorn.run(app, host=host, port=port)

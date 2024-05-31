from fastapi import FastAPI
import uvicorn


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

    uvicorn.run(app, host=host, port=port)

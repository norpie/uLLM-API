from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/ping")
def ping():
    return "pong"

def run(host, port, model_manager):
    uvicorn.run(app, host=host, port=port)

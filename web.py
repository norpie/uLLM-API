from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/ping")
def ping():
    return "pong"

def run(host, port, data_dir):
    uvicorn.run(app, host=host, port=port)

from websockets.asyncio.server import ServerConnection, serve
from websockets.protocol import State
from engines.engine import EngineParameters
from models import ModelManager

import asyncio
import websockets
import json


def ping():
    return "pong"


async def respond_error(websocket: ServerConnection, id: str | None, message: str):
    response = json.dumps({"id": id, "error": message})
    if websocket.state == State.OPEN:
        await websocket.send("\n" + response)


async def respond(websocket: ServerConnection, id: str | None, result: dict):
    response = json.dumps({"id": id, "result": result})
    if websocket.state == State.OPEN:
        await websocket.send("\n" + response)


async def complete_handler(
    websocket: ServerConnection,
    id: str,
    snippet: str,
    parameters: EngineParameters,
    model_manager: ModelManager,
):
    async def streaming_callback(tokens):
        if websocket.state == State.OPEN:
            await respond(websocket, id, {"status": "ongoing", "tokens": tokens})

    current_engine = model_manager.current_engine()

    if current_engine is None:
        await respond_error(websocket, id, "No model loaded")
        return

    final = await current_engine.complete_streaming(
        parameters,
        snippet,
        streaming_callback,
    )
    if websocket.state == State.OPEN:
        await respond(websocket, id, {"status": "final", "tokens": final})


async def handler(websocket: ServerConnection, model_manager: ModelManager):
    try:
        async for message in websocket:
            try:
                parsed = json.loads(message)
                id = parsed.get("id")
                params = parsed.get("params")
                match parsed["method"]:
                    case "complete":
                        parameters = EngineParameters.from_dict(params.get("engine_parameters"))
                        await complete_handler(
                            websocket, id, params["snippet"], parameters, model_manager
                        )
                    case "cancel":
                        engine = model_manager.current_engine()
                        if engine is not None:
                            engine.cancel_streaming()
                            await respond(websocket, id, {"status": "cancelled"})
                        else:
                            await respond_error(websocket, id, "No model loaded")
                    case "ping":
                        await respond(websocket, id, {"status": "pong"})
                    case "status":
                        await respond(
                            websocket,
                            id,
                            {"status": model_manager.model_status()},
                        )
                    case "list_models":
                        await respond(
                            websocket, id, {"models": model_manager.list_models()}
                        )
                    case "load_model":
                        await respond(
                            websocket, id, {"status": model_manager.model_status()}
                        )
                        model_manager.load_model(params["engine"], params["model"])
                    case _:
                        await respond_error(websocket, id, "Unknown method")
            except Exception as e:
                await respond_error(websocket, None, str(e))
    except websockets.exceptions.ConnectionClosedError:
        pass


def start(host: str, port: int, model_manager: ModelManager):
    import threading

    thread = threading.Thread(target=task, args=(host, port, model_manager))
    thread.start()


def task(host: str, port: int, model_manager: ModelManager):
    return asyncio.run(run(host, port, model_manager))


async def run(host: str, port: int, model_manager: ModelManager):
    server = await serve(lambda ws: handler(ws, model_manager), host, port)
    await server.serve_forever()

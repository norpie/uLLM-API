import websockets
import asyncio
import json


def ping():
    return "pong"


async def respond_error(websocket, id, message):
    response = json.dumps({"id": id, "error": message})
    if websocket.open:
        await websocket.send("\n" + response)


async def respond(websocket, id, result):
    response = json.dumps({"id": id, "result": result})
    if websocket.open:
        await websocket.send("\n" + response)


async def complete_handler(websocket, id, snippet, model_manager):
    async def streaming_callback(tokens):
        if websocket.open:
            await respond(websocket, id, {"status": "ongoing", "tokens": tokens})

    final = await model_manager.current_engine().complete_streaming(
        snippet,
        streaming_callback,
    )
    if websocket.open:
        await respond(websocket, id, {"status": "final", "tokens": final})


async def handler(websocket, _, model_manager):
    try:
        async for message in websocket:
            try:
                parsed = json.loads(message)
            except Exception as e:
                await respond_error(websocket, None, f"JSON Decode error: {str(e)}")
                continue
            id = parsed.get("id")
            params = parsed.get("params")
            match parsed["method"]:
                case "complete":
                    await complete_handler(
                        websocket, id, params["snippet"], model_manager
                    )
                case "ping":
                    await respond(websocket, id, {"status": "pong"})
                case "list_models":
                    await respond(
                        websocket, id, {"models": model_manager.list_models()}
                    )
                case "load_model":
                    try:
                        model_manager.load_model(params["engine"], params["model"])
                        await respond(websocket, id, {"status": "success"})
                    except Exception as e:
                        await respond_error(websocket, id, str(e))
                case _:
                    await respond_error(websocket, id, "Unknown method")
    except websockets.exceptions.ConnectionClosedError:
        pass


def start(host, port, model_manager):
    import threading

    thread = threading.Thread(target=run, args=(host, port, model_manager))
    thread.start()


def run(host, port, model_manager):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = loop.run_until_complete(
        websockets.serve(lambda ws, path: handler(ws, path, model_manager), host, port)
    )

    print(f"WebSocket server started on {host}:{port}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()

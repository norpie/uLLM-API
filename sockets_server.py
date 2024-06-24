import websockets
import threading
import asyncio
import time
from websockets.server import serve


def start(host, port, model_manager):
    import threading

    thread = threading.Thread(target=run, args=(host, port, model_manager))
    thread.start()


# WebSocket handler
async def echo_handler(websocket, path):
    async for message in websocket:
        print(f"Received message: {message}")
        await websocket.send(f"Echo: {message}")


# Synchronous wrapper for the async server
def sync_websocket_server(host, port, model_manager):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    server = loop.run_until_complete(websockets.serve(echo_handler, host, port))

    print(f"WebSocket server started on {host}:{port}")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()


def run(host, port, model_manager):
    sync_websocket_server(host, port, model_manager)

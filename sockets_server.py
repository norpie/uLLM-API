import asyncio
import websockets

from request import IResponder, Request, Response
from websockets.asyncio.server import ServerConnection, serve
from websockets.protocol import State
from models import ModelManager


class SocketResponder(IResponder):
    def __init__(self, websocket: ServerConnection):
        self.websocket = websocket

    async def raw_response(self, response: Response):
        if self.websocket.state == State.OPEN:
            await self.websocket.send("\n" + response.toJSON())

    async def response(self, response: Response):
        await self.raw_response(response)

    async def intermediate_response(self, response: Response):
        await self.raw_response(response)


async def handler(websocket: ServerConnection, model_manager: ModelManager):
    responder = SocketResponder(websocket)
    try:
        async for message in websocket:
            try:
                request = Request.from_json(message)
                await request.handle(model_manager, responder)
            except Exception as e:
                await Response.new_no_id_error(str(e)).send(responder)
    except websockets.exceptions.ConnectionClosedError:
        pass


def start(host: str, port: int, model_manager: ModelManager):
    import threading

    thread = threading.Thread(target=task, args=(host, port, model_manager))
    thread.start()


def task(host: str, port: int, model_manager: ModelManager):
    return asyncio.run(run(host, port, model_manager))


async def run(host: str, port: int, model_manager: ModelManager):
    print(f"Starting sockets server on {host}:{port}")
    server = await serve(lambda ws: handler(ws, model_manager), host, port)
    await server.serve_forever()

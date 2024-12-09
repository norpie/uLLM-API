import json

from dataclasses import dataclass
from engines.engine import Engine, EngineParameters
from models import ModelManager
from typing import Optional, Union


@dataclass
class Request:
    id: Optional[str] = None
    method: Optional[str] = None
    params: Optional[dict] = None

    async def param_gate(
        self, params: dict | None, keys: list[str]
    ) -> Union["Response", None]:
        if self.id is None:
            return Response.new_no_id_error("No id provided")
        if params is None:
            return Response.new_no_id_error("No params provided")
        for key in keys:
            if key not in params:
                return Response.new_error(self.id, f"No `{key}` provided")
        return None

    async def handle(
        self, model_manager: ModelManager, responder: "IResponder"
    ) -> "Response":
        if self.id is None:
            return await Response.new_no_id_error("No id provided").send(responder)
        id: str = self.id
        if self.method is None:
            return await Response.new_error(id, "No method provided").send(responder)
        method: str = self.method
        try:
            match method:
                case "complete":
                    error = await self.param_gate(
                        self.params, ["prompt", "engine_parameters"]
                    )
                    if error is not None:
                        return await error.send(responder)

                    prompt: str = self.params["prompt"]  # type: ignore
                    engine_parameters: EngineParameters = EngineParameters.from_json(
                        self.params["engine_parameters"]  # type: ignore
                    )

                    async def streaming_callback(tokens):
                        response = Response.new_result(
                            id, {"status": "ongoing", "tokens": tokens}
                        )
                        await responder.intermediate_response(response)

                    current_engine = model_manager.current_engine()
                    if current_engine is None:
                        return await Response.new_error(id, "No model loaded").send(
                            responder
                        )
                    final = await current_engine.complete_streaming(
                        engine_parameters,
                        prompt,
                        streaming_callback,
                    )
                    return await Response.new_result(
                        id, {"status": "final", "tokens": final}
                    ).send(responder)
                case "cancel":
                    current_engine = model_manager.current_engine()
                    if current_engine is not None:
                        current_engine.cancel_streaming()
                        return await Response.new_result(
                            id, {"status": "cancelled"}
                        ).send(responder)
                    else:
                        return await Response.new_result(
                            id, {"status": "unloaded"}
                        ).send(responder)
                case "ping":
                    return await Response.new_result(id, {"status": "pong"}).send(
                        responder
                    )
                case "status":
                    return await Response.new_result(
                        id, model_manager.model_status()
                    ).send(responder)
                case "list_models":
                    return await Response.new_result(
                        id, {"models": model_manager.list_models()}
                    ).send(responder)
                case "unload_model":
                    await responder.intermediate_response(
                        Response.new_result(id, model_manager.model_status())
                    )
                    model_manager.unload_model()
                    return await Response.new_result(
                        id, model_manager.model_status()
                    ).send(responder)
                case "load_model":
                    error = await self.param_gate(self.params, ["engine", "model"])
                    if error is not None:
                        return await error.send(responder)
                    await responder.intermediate_response(
                        Response.new_result(
                            id,
                            {
                                "status": "unloading",
                                "model": model_manager.model_status().get("model"),
                                "engine": model_manager.model_status().get("engine"),
                            },
                        )
                    )
                    model_manager.unload_model()
                    await responder.intermediate_response(
                        Response.new_result(
                            id,
                            model_manager.model_status(),
                        )
                    )
                    await responder.intermediate_response(
                        Response.new_result(
                            id,
                            {
                                "status": "loading",
                                "model": self.params["model"],  # type: ignore
                                "engine": self.params["engine"],  # type: ignore
                            },
                        )
                    )
                    engine = Engine.from_str(self.params["engine"])  # type: ignore
                    model = self.params["model"]  # type: ignore
                    model_manager.load_model(engine, model)
                    return await Response.new_result(
                        id, model_manager.model_status()
                    ).send(responder)
                case _:
                    return await Response.new_error(id, "Unknown method").send(
                        responder
                    )
        except Exception as e:
            return await Response.new_error(id, str(e)).send(responder)

    @staticmethod
    def from_json(json) -> "Request":
        data = json.loads(json)
        return Request(**data)


@dataclass
class Response:
    id: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None

    def __init__(self, id: str | None, result: dict | None, error: str | None):
        self.id = id
        self.result = result
        self.error = error

    async def send(self, responder: "IResponder") -> "Response":
        await responder.response(self)
        return self

    @staticmethod
    def new_no_id_error(error: str) -> "Response":
        return Response(None, None, error)

    @staticmethod
    def new_result(id: str, result: dict) -> "Response":
        return Response(id, result, None)

    @staticmethod
    def new_error(id: str, error: str) -> "Response":
        return Response(id, None, error)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class IResponder:
    model_manager: ModelManager

    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager

    async def intermediate_response(self, response: Response):
        pass

    async def response(self, response: Response):
        pass

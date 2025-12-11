import importlib
import json
import logging
from typing import Callable

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from .element import Root
from .rendering import HTMLRenderer

Page = Callable[[], Root]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def serve_stub(title: str = "provectus app", websocket_endpoint: str = "/") -> str:
    return f"""
<html>
<head>
    <title>{title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.4" integrity="sha384-1RwI/nvUSrMRuNj7hX1+27J8XDdCoSLf0EjEyF69nacuWyiJYoQ/j39RT1mSnd2G" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/idiomorph@0.7.4/dist/idiomorph-ext.min.js" integrity="sha384-SsScJKzATF/w6suEEdLbgYGsYFLzeKfOA6PY+/C5ZPxOSuA+ARquqtz/BZz9JWU8" crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body hx-ext="ws, morph" ws-connect="{websocket_endpoint}">
    <div id="root">loading...</div>
</body>
"""


class App(Starlette):
    """
    Starlette application that serves a WebSocket-driven Provecta UI.

    Parameters
    ----------
    app_dir:
        The Python package/module path where your application pages live,
        e.g. ``"app"`` when you have an ``app/home.py`` module exposing
        a ``page() -> Root`` function.
    hot_reload:
        Reserved for future hot-reload behaviour; currently unused but
        kept for backwards compatibility.
    """

    def __init__(self, app_dir: str = "app", hot_reload: bool = False, **kwargs):
        self.app_dir = app_dir
        self.hot_reload = hot_reload

        routes = [
            Route("/", endpoint=self.serve_initial_html, methods=["GET"]),
            WebSocketRoute("/", endpoint=self.websocket_endpoint),
        ]

        super().__init__(routes=routes, **kwargs)

    async def serve_initial_html(self, request):
        return HTMLResponse(serve_stub())

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()

        renderer = HTMLRenderer()
        homepage: Page = importlib.import_module(f"{self.app_dir}.home").page
        root = homepage()
        rendered = renderer.render(root)
        logger.debug(f"rendered: {rendered}")
        await websocket.send_text(rendered)

        try:
            while True:
                data = await websocket.receive_text()
                data = json.loads(data)
                logger.debug(data)
                trigger = data["trigger"] if "trigger" in data else ""
                source = (
                    root._id_store[(data["HEADERS"]["HX-Trigger"])]
                    if root._id_store
                    else None
                )
                target = (
                    root._id_store[(data["HEADERS"]["HX-Target"])]
                    if root._id_store
                    else None
                )
                if source is not None and target is not None:
                    target._event(source, trigger, root, data)
                    rendered = renderer.render(root)
                    logger.debug(f"rendered: {rendered}")
                    await websocket.send_text(rendered)

        except WebSocketDisconnect:
            return

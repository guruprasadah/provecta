import importlib
import json
from typing import Callable

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route, WebSocketRoute
from starlette.websockets import WebSocket, WebSocketDisconnect

from element import Root
from rendering import HTMLRenderer

Page = Callable[[], Root]


async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    renderer = HTMLRenderer()
    homepage: Page = importlib.import_module("app.home").page
    root = homepage()
    await websocket.send_text(renderer.render(root))

    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            trigger = data["trigger"]
            source = root._id_store[int(data["HEADERS"]["HX-Trigger"])]
            target = root._id_store[int(data["HEADERS"]["HX-Target"])]
            target._event(source, trigger)
            await websocket.send_text(renderer.render(root))

    except WebSocketDisconnect:
        return


def serve_stub(title: str = "provectus app", websocket_endpoint: str = "/") -> str:
    return f"""
<html>
<head>
    <title>{title}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/htmx.org@2.0.8/dist/htmx.min.js" integrity="sha384-/TgkGk7p307TH7EXJDuUlgG3Ce1UVolAOFopFekQkkXihi5u/6OCvVKyz1W+idaz" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/htmx-ext-ws@2.0.4" integrity="sha384-1RwI/nvUSrMRuNj7hX1+27J8XDdCoSLf0EjEyF69nacuWyiJYoQ/j39RT1mSnd2G" crossorigin="anonymous"></script>
    <script src="https://unpkg.com/htmx-ext-morphdom-swap@2.0.0/morphdom-swap.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body hx-ext="ws, morphdom-swap" ws-connect="{websocket_endpoint}">
    <div id="root" hx-swap="morphdom">loading...</div>
</body>
"""


async def serve_initial_html(request):
    return HTMLResponse(serve_stub())


app = Starlette(
    routes=[
        WebSocketRoute("/", websocket_endpoint),
        Route("/", serve_initial_html),
    ]
)

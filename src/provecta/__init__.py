"""
Provecta
========

A small, minimal experiment in building an HTMX + WebSocket–driven UI
framework in Python, written out of both curiosity and a healthy aversion
to JavaScript-heavy frontends.

This package exposes a thin public API around the internal building blocks:
    - the Starlette-based `App` server
    - the element tree primitives (e.g. `Element`, `Container`, `Root`)
    - the HTML renderer
"""

from .element import (
    Button,
    ButtonType,
    Container,
    Element,
    Form,
    Image,
    Input,
    Root,
    Text,
    TextInput,
    TextInputType,
)
from .framework import App, serve_stub
from .rendering import HTMLRenderer

__all__ = [
    # Server
    "App",
    "serve_stub",
    # Core element primitives
    "Element",
    "Container",
    "Root",
    "Form",
    "Text",
    "Image",
    "Input",
    "TextInput",
    "TextInputType",
    "Button",
    "ButtonType",
    "EventResult",
    # Rendering
    "HTMLRenderer",
]

__version__ = "0.1.0"

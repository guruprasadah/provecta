import logging
from dataclasses import dataclass, field, fields
from enum import Enum
from typing import Any

from .element import (
    Container,
    Element,
)

logger = logging.getLogger(__name__)


class Renderer:
    def render(self, base: Element) -> Any:
        raise NotImplementedError


class HTMLRenderer(Renderer):
    @dataclass
    class Node:
        tag: str
        attribs: dict[str, str]
        body: str = field(default="")
        children: list["HTMLRenderer.Node"] = field(default_factory=list)

    _old_vdom: "HTMLRenderer.Node"

    def _build_vdom(
        self,
        element: Element,
    ) -> "HTMLRenderer.Node":
        attribs: dict[str, str] = {}
        body: str = ""
        children: list["HTMLRenderer.Node"] = []

        attribs["id"] = element._get_id()

        if not element._dirty:
            attribs["hx-preserve"] = "true"
        else:
            for f in fields(element):
                if data := f.metadata:
                    if data["attribute"]:
                        attribs[data.get("actual", f.name)] = self._render_attribute(
                            getattr(element, f.name)
                        )
                    else:
                        body = body + getattr(element, f.name)

                    if attribs.get("hx-trigger"):
                        attribs["ws-send"] = "true"
            element._dirty = False
            if isinstance(element, Container):
                children = [self._build_vdom(child) for child in element._children]
            else:
                children = []

        return self.Node(element._tag, attribs, body, children)

    def _render_attribute(self, attribute) -> str:
        if isinstance(attribute, bool):
            return "true" if attribute else "false"
        elif isinstance(attribute, Enum):
            return attribute.value
        else:
            return str(attribute)

    def _render_vdom(
        self, node: "HTMLRenderer.Node", render_children: bool = True
    ) -> str:
        return f"""<{node.tag} {" ".join([f"{k} = '{v}'" for k, v in node.attribs.items()])} > {node.body} {("".join([self._render_vdom(child) for child in node.children])) if render_children else ""} </{node.tag}> """

    def render(self, base: Element) -> str:
        vdom = self._build_vdom(base)
        vdom.attribs["hx-swap-oob"] = "morph"
        self._old_vdom = vdom
        return self._render_vdom(vdom)

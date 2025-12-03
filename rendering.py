from dataclasses import dataclass, field
from typing import Any

from element import (
    Button,
    Container,
    Element,
    Form,
    Image,
    Input,
    Root,
    Text,
    TextInput,
    _element_default_update,
)


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

    _old_vdom: Node

    def _build_vdom(
        self,
        base: Element,
        stub_children: bool = False,
        stub: bool = False,
    ) -> Node:
        attribs = {}
        if stub:
            attribs["id"] = id(base)
            attribs["hx-preserve"] = "true"
        else:
            attribs = self._build_attribs(base)
        if isinstance(base, Text):
            return self.Node(
                "span",
                attribs,
                base.content if not stub else "",
            )
        elif isinstance(base, Image):
            if not stub:
                attribs["src"] = base.src
            return self.Node("img", attribs)
        elif isinstance(base, Container):
            if stub:
                children = []
            else:
                children = [
                    self._build_vdom(x, stub=stub_children) for x in base.children
                ]
            tag = "div"
            if isinstance(base, Root):
                attribs["id"] = "root"
            elif isinstance(base, Form):
                tag = "form"
            return self.Node(
                tag,
                attribs,
                children=children,
            )
        elif isinstance(base, Input):
            tag = "input"
            attribs["name"] = base.name
            if isinstance(base, TextInput):
                attribs["type"] = base.type.value
                attribs["required"] = "true" if base.required else "false"
                attribs["type"] = base.type.value
                attribs["value"] = base.value
                attribs["placeholder"] = base.placeholder
                attribs["min_length"] = str(base.min_length)
                (
                    attribs.setdefault("max_length", str(base.max_length))
                    if base.max_length is not None
                    else None
                )
                (
                    attribs.setdefault("size", str(base.size))
                    if base.size is not None
                    else None
                )
                return self.Node(tag, attribs)
            elif isinstance(base, Button):
                tag = "button"
                attribs["type"] = base.type.value
                return self.Node(tag, attribs, base.content)
            return self.Node("dummy, unreachable", {})

        else:
            raise TypeError(
                "VDOM building for this element type is not implemented yet"
            )

    def _build_attribs(self, base: Element) -> dict[str, str]:
        attribs: dict[str, str] = {}
        attribs["id"] = str(id(base))
        if base.trigger:
            attribs["hx-trigger"] = base.trigger
            attribs["hx-vals"] = (
                'js:{"trigger": typeof event !== "undefined" ? event.type : "no_event_data"}'
            )
        if base.trigger or base.update is not _element_default_update:
            attribs["ws-send"] = "true"
        if base.style:
            attribs["class"] = base.style
        return attribs

    def _render_vdom(self, node: Node, render_children: bool = True) -> str:
        return f"""<{node.tag} {" ".join([f"{k} = '{v}'" for k, v in node.attribs.items()])} > {node.body} {("".join([self._render_vdom(child) for child in node.children])) if render_children else ""} </{node.tag}> """

    def render(self, base: Element, stub_children: bool = False) -> str:
        vdom = self._build_vdom(base, stub_children)
        vdom.attribs["hx-swap-oob"] = "morph"
        self._old_vdom = vdom
        return self._render_vdom(vdom)

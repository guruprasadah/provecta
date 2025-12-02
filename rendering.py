from dataclasses import dataclass, field
from typing import Any

from element import Container, Element, Image, Root, Text


class Renderer:
    def render(self, base: Element) -> Any:
        raise NotImplementedError


class HTMLRenderer(Renderer):
    def _generic_attribs(self, base: Element, base_id: str = "") -> str:
        return (
            f"""id="{base_id if base_id else id(base)}" class="{base.style}" """
            + (
                f"""hx-trigger="{base.trigger}" hx-vals='js:{{"trigger": event.type}}' """
                if base.trigger
                else ""
            )
            + ("ws-send " if base.trigger or base.update else "")
        )

    def _container(
        self,
        base: Container,
        tag: str = "div",
        extra_attribs: str = "",
        base_id: str = "",
    ) -> str:
        return (
            f"""<{tag} {self._generic_attribs(base, base_id=base_id)}{extra_attribs}>\n """
            + "\n".join(self.render(child) for child in base.children)
            + f"\n</{tag}>"
        )

    def render(self, base: Element) -> str:
        if isinstance(base, Text):
            return f"""<span {self._generic_attribs(base)}>{base.content}</span>"""
        elif isinstance(base, Image):
            return f"""<img {self._generic_attribs(base)} src="{base.src}" />"""
        elif isinstance(base, Root):
            return self._container(
                base, extra_attribs="""hx-swap="morphdom" """, base_id="root"
            )
        elif isinstance(base, Container):
            return self._container(base)
        else:
            raise TypeError("Rendering for this element type is not implemented yet")

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

ElementIDStore = dict[int, "Element"]


@dataclass
class Element:
    style: str = field(default="", kw_only=True)
    trigger: str = field(default="", kw_only=True)
    update: Optional[Callable[[Any, Any, str], bool]] = field(
        default=None, kw_only=True
    )
    state: dict[str, Any] = field(default_factory=dict[str, Any], kw_only=True)

    parent: Optional["Container"] = field(default=None, kw_only=True)

    def use_state(self, name: str, default: Any) -> tuple[Any, Callable[[Any], None]]:
        if name not in self.state:
            self.state[name] = default

        def set(value) -> None:
            self.state[name] = value

        return self.state[name], set

    def _event(self, source: Any, trigger: str) -> bool:
        if self.update and self.update(self, source, trigger):
            return True
        elif self.parent:
            return self.parent._event(source, trigger)
        else:
            return False

    def _register_self(self, store: ElementIDStore) -> None:
        store[id(self)] = self


@dataclass
class Text(Element):
    content: str = ""


@dataclass
class Image(Element):
    style: str = field(default="h-full object-contain", kw_only=True)
    src: str = ""


@dataclass
class Container(Element):
    children: list[Element] = field(default_factory=list[Element])
    _id_store: Optional[ElementIDStore] = field(default=None, kw_only=True)

    def __post_init__(self):
        for child in self.children:
            child.parent = self

    def add(self, child: Element):
        child.parent = self
        child._register_self(self._id_store) if self._id_store is not None else None
        self.children.append(child)

    def _register_self(self, store: ElementIDStore) -> None:
        store[id(self)] = self
        self._id_store = store
        for child in self.children:
            child._register_self(self._id_store)


@dataclass
class Root(Container):
    def __post_init__(self):
        self._id_store = ElementIDStore()
        self._id_store[id(self)] = self
        for child in self.children:
            child.parent = self
            child._register_self(self._id_store)

    def _register_self(self, store: ElementIDStore) -> None:
        raise NotImplementedError("Root elements cannot be children")

    def _event(self, source: Any, trigger: str) -> bool:
        print("unhandled event with trigger", trigger)
        return False

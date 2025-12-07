import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


ElementIDStore = dict[int, "Element"]


class EventResult(Enum):
    NOT_HANDLED = auto()
    MUTATE_SELF = auto()
    MUTATE_CHILDREN = auto()
    MUTATE_PARENT = auto()
    MUTATE_ALL = auto()


def _element_default_update(x, y, z, w):
    return EventResult.NOT_HANDLED


@dataclass
class Element:
    style: str = field(default="", kw_only=True)
    trigger: str = field(default="", kw_only=True)
    update: Callable[[Any, Any, Any, str], EventResult] = field(
        default=_element_default_update, kw_only=True
    )
    state: dict[str, Any] = field(default_factory=dict[str, Any], kw_only=True)

    _dirty: bool = field(default=False, kw_only=True)

    parent: Optional["Container"] = field(default=None, kw_only=True)

    def setup(self):
        pass

    def use_state(self, name: str, default: Any) -> tuple[Any, Callable[[Any], None]]:
        if name not in self.state:
            self.state[name] = default

        def get() -> Any:
            return self.state[name]

        def set(value) -> None:
            self._dirty = True
            self.state[name] = value

        return get, set

    def remove_self(self):
        if self.parent:
            for i, child in enumerate(self.parent._children):
                if child is self:
                    del self.parent._children[i]
                    break
            else:
                logger.warning(
                    f"id {id(self)} has a parent but parent doesn't store reference to it. something is seriously wrong"
                )

    def _event_preupdate(self, data: dict):
        pass

    def _event(
        self, source: Any, trigger: str, root: "Root", data: dict
    ) -> tuple[EventResult, "Element"]:
        self._event_preupdate(data)
        if (
            self.update
            and (result := self.update(self, source, root, trigger))
            != EventResult.NOT_HANDLED
        ):
            return result, self
        elif self.parent:
            return self.parent._event(source, trigger, root, data)
        else:
            return EventResult.NOT_HANDLED, self

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
class Input(Element):
    name: str = field()

    def setup(self):
        top = self.parent
        while top is not None:
            if isinstance(top, Form):
                top.fields[self.name] = self
                break
            else:
                top = top.parent
        else:
            logger.warning("Input not descendant of Form")


class TextInputType(Enum):
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    URL = "url"
    SEARCH = "search"
    TEL = "tel"


@dataclass
class TextInput(Input):
    required: bool = field(default=False, kw_only=True)
    type: TextInputType = field(default=TextInputType.TEXT, kw_only=True)
    value: str = field(default="", kw_only=True)
    placeholder: str = field(default="", kw_only=True)
    min_length: int = field(default=0, kw_only=True)
    max_length: Optional[int] = field(default=None, kw_only=True)
    size: Optional[int] = field(default=None, kw_only=True)

    def _event_preupdate(self, data: dict):
        if self.name in data:
            self.value = data[self.name]


class ButtonType(Enum):
    BUTTON = "button"
    SUBMIT = "submit"
    RESET = "reset"


@dataclass
class Button(Input):
    type: ButtonType = field(default=ButtonType.BUTTON)
    content: str = field(default="")


@dataclass
class Container(Element):
    _children: list[Element] = field(default_factory=list[Element])
    _id_store: Optional[ElementIDStore] = field(default=None, kw_only=True)

    def setup(self):
        for child in self._children:
            child.setup()

    def __post_init__(self):
        for child in self._children:
            child.parent = self

    def add(self, child: Element):
        self._dirty = True
        child.parent = self
        child._register_self(self._id_store) if self._id_store is not None else None
        self._children.append(child)

    def _register_self(self, store: ElementIDStore) -> None:
        store[id(self)] = self
        self._id_store = store
        for child in self._children:
            child._register_self(self._id_store)


@dataclass
class Root(Container):
    def __post_init__(self):
        self._id_store = ElementIDStore()
        self._id_store[id(self)] = self
        for child in self._children:
            child.parent = self
            child._register_self(self._id_store)
        self.setup()

    def _register_self(self, store: ElementIDStore) -> None:
        raise NotImplementedError("Root elements cannot be children")

    def _event(
        self, source: Any, trigger: str, root: "Root", data: dict
    ) -> tuple[EventResult, Element]:
        logger.info(f"unhandled event with trigger: {trigger}")
        return EventResult.NOT_HANDLED, self

    def load_into(self, new_root: "Root"):
        for child in self._children:
            child.parent = None
        self._children = new_root._children
        self.__post_init__()


@dataclass
class Form(Container):
    trigger: str = field(default="submit", kw_only=True)
    fields: dict[str, Input] = field(default_factory=dict[str, Input], kw_only=True)

    def _event_preupdate(self, data: dict):
        for key, value in data.items():
            if key in self.fields:
                field = self.fields[key]
                if isinstance(field, TextInput):
                    field.value = value

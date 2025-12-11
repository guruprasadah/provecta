import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional, TypedDict

logger = logging.getLogger(__name__)


ElementIDStore = dict[str, "Element"]


class EventResult(Enum):
    NOT_HANDLED = auto()
    MUTATE_SELF = auto()
    MUTATE_CHILDREN = auto()
    MUTATE_PARENT = auto()
    MUTATE_ALL = auto()


def _element_default_update(x, y, z, w):
    return False


@dataclass
class Element:
    _tag: str = field(default="", kw_only=True)
    style: str = field(
        default="",
        metadata={"attribute": True, "actual": "class"},
        kw_only=True,
    )
    trigger: str = field(
        default="",
        metadata={
            "attribute": True,
            "actual": "hx-trigger",
        },
        kw_only=True,
    )
    update: Callable[[Any, Any, Any, str], bool] = field(
        default=_element_default_update, kw_only=True
    )
    state: dict[str, Any] = field(default_factory=dict[str, Any], kw_only=True)

    _dirty: bool = field(default=True, kw_only=True)

    parent: Optional["Container"] = field(default=None, kw_only=True)

    def setup(self):
        pass

    def use_state(self, name: str, default: Any) -> tuple[Any, Callable[[Any], None]]:
        if name not in self.state:
            self.state[name] = default

        def get() -> Any:
            return self.state[name]

        def set(value) -> None:
            self._set_dirty()
            self.state[name] = value

        return get, set

    def remove_self(self):
        if self.parent:
            self.parent._children = [
                child for child in self.parent._children if child is not self
            ]
            self.parent._set_dirty()

    def _get_id(self) -> str:
        return str(id(self))

    def _event_preupdate(self, data: dict):
        pass

    def _event(self, source: Any, trigger: str, root: "Root", data: dict) -> None:
        self._event_preupdate(data)
        if self.update:
            self.update(self, source, root, trigger)
        elif self.parent:
            self.parent._event(source, trigger, root, data)

    def _register_self(self, store: ElementIDStore) -> None:
        store[self._get_id()] = self

    def _set_dirty(self):
        self._dirty = True
        if self.parent:
            self.parent._set_dirty()


@dataclass
class Text(Element):
    _tag: str = field(default="span", kw_only=True)
    content: str = field(default="", metadata={"attribute": False})


@dataclass
class Image(Element):
    _tag: str = field(default="img", kw_only=True)
    style: str = field(
        default="h-full object-contain",
        metadata={"attribute": True, "actual": "class"},
        kw_only=True,
    )
    src: str = field(default="", metadata={"attribute": True})


@dataclass
class Input(Element):
    name: str = field(metadata={"attribute": True})

    def setup(self):
        top = self.parent
        while top is not None:
            if isinstance(top, Form):
                top.input_fields[self.name] = self
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
    _tag: str = field(default="input", kw_only=True)
    required: bool = field(default=False, metadata={"attribute": True}, kw_only=True)
    type: TextInputType = field(
        default=TextInputType.TEXT, metadata={"attribute": True}, kw_only=True
    )
    value: str = field(default="", metadata={"attribute": True}, kw_only=True)
    placeholder: str = field(default="", metadata={"attribute": True}, kw_only=True)
    min_length: int = field(
        default=0, metadata={"attribute": True, "actual": "minlength"}, kw_only=True
    )
    max_length: Optional[int] = field(
        default=None, metadata={"attribute": True, "actual": "maxlength"}, kw_only=True
    )
    size: Optional[int] = field(
        default=None, metadata={"attribute": True}, kw_only=True
    )

    def _event_preupdate(self, data: dict):
        if self.name in data:
            self.value = data[self.name]


class ButtonType(Enum):
    BUTTON = "button"
    SUBMIT = "submit"
    RESET = "reset"


@dataclass
class Button(Input):
    _tag: str = field(default="button", kw_only=True)
    type: ButtonType = field(default=ButtonType.BUTTON, metadata={"attribute": True})
    content: str = field(default="", metadata={"attribute": False})


@dataclass
class Container(Element):
    _tag: str = field(default="div", kw_only=True)
    _children: list[Element] = field(default_factory=list[Element])
    _id_store: Optional[ElementIDStore] = field(default=None, kw_only=True)

    def setup(self):
        for child in self._children:
            child.setup()

    def __post_init__(self):
        for child in self._children:
            child.parent = self

    def add(self, child: Element):
        self._set_dirty()
        child.parent = self
        child._register_self(self._id_store) if self._id_store is not None else None
        self._children.append(child)

    def _register_self(self, store: ElementIDStore) -> None:
        super()._register_self(store)
        self._id_store = store
        for child in self._children:
            child._register_self(self._id_store)


@dataclass
class Root(Container):
    def __post_init__(self):
        self._id_store = ElementIDStore()
        self._id_store[self._get_id()] = self
        for child in self._children:
            child.parent = self
            child._register_self(self._id_store)
        self.setup()

    def _get_id(self) -> str:
        return "root"

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
    _tag: str = field(default="form", kw_only=True)
    trigger: str = field(
        default="submit",
        metadata={"attribute": True, "actual": "hx-trigger"},
        kw_only=True,
    )
    input_fields: dict[str, Input] = field(
        default_factory=dict[str, Input], kw_only=True
    )

    def _event_preupdate(self, data: dict):
        for key, value in data.items():
            if key in self.input_fields:
                field = self.input_fields[key]
                if isinstance(field, TextInput):
                    field.value = value

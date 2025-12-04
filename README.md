![Provecta logo](./logo.png)

Provecta is a small, minimal experiment in building an **HTMX + WebSocket-driven UI framework in Python**, written out of both curiosity and a healthy aversion to JS.

This project is intentionally tiny, toy-ish, and educational: something between a tech demo, a playground for architectural ideas, and a portfolio-friendly showcase of clean modular design.

## ✨ Features

- **Declarative UI tree** built on Python classes
- **Reactive events** with bubbling included
- **Zero page-reload interactions** powered by HTMX and WebSockets
- **Tiny VDOM renderer** that morphs DOM nodes via idiomorph
- **A simple app structure** demonstrating routing via state updates
- **Hot-reload friendly server** using Starlette and Uvicorn
- **TailwindCSS** support via CDN for quick styling

## 🚀 How it Works

Provecta renders a Python-defined element tree into HTML, and sends it to the browser through the established WebSocket.

When an event is received, we:
1. Locate the triggering element using an ID store.
2. Route the event to it, bubbling if necessary.
3. Compute morph-friendly changes to the DOM based on the ```EventResult```
4. Render and send said changes via WebSocket, resulting in a page update using HTMX's out-of-band swaps.

The browser only has to render HTML and fire events, keeping the frontend pleasantly lightweight.

## 📦 Installation

Once published, you will be able to install Provecta from PyPI:

```bash
pip install provecta
```

For local development (this repository), you can also use:

```bash
pip install -e .
```

## 🧰 Basic Usage

After installation, you can build an app using the `provecta` package:

```python
from provecta import App, Root, Container, Button, ButtonType, Text, EventResult


def button_click(this: Button, source: Button, root: Root, trigger: str) -> EventResult:
    click_count, set_click_count = this.use_state("click_count", 0)
    set_click_count(click_count + 1)
    if click_count + 1 < 10:
        this.parent.add(Text(f"this was added on click number {click_count + 1}"))
        return EventResult.MUTATE_PARENT
    else:
        root.load_into(Root([Text("you clicked the button too many times blud")]))
        return EventResult.MUTATE_ALL


def page() -> Root:
    return Root(
        [
            Container(
                [
                    Container(
                        [
                            Button(
                                name="button",
                                content="Click me!",
                                type=ButtonType.BUTTON,
                                style="h-8 w-full bg-blue-600 text-white transition-all duration-300 hover:bg-zinc-200 hover:text-black rounded-sm hover:rounded-none",
                                trigger="click",
                                update=button_click,
                            )
                        ],
                        style="flex flex-col",
                    )
                ],
                style="m-auto",
            )
        ],
        style="flex h-screen",
    )


app = App(app_dir="app")
```

Point your `app/home.py` module at the `page` function above, then run Uvicorn
against the Provecta `app` instance.

Minimal Example:

**`app/home.py`**
```python
# State lives in elements, events mutate the tree, and returning an EventResult tells Provecta what to re-render.
def button_click(this: Button, source: Button, root: Root, trigger: str) -> EventResult:
    click_count, set_click_count = this.use_state("click_count", 0)
    set_click_count(click_count + 1)
    if click_count + 1 < 10:
        this.parent.add(Text(f"this was added on click number {click_count + 1}"))
        return EventResult.MUTATE_PARENT
    else:
        root.load_into(Root([Text("you clicked the button too many times blud")])) # Load into a new page
        return EventResult.MUTATE_ALL


def page() -> Root:
    return Root(
        [
            Container(
                [
                    Container(
                        [
                            Button(
                                name="button",
                                content="Click me!",
                                type=ButtonType.BUTTON,
                                style="h-8 w-full bg-blue-600 text-white transition-all duration-300 hover:bg-zinc-200 hover:text-black rounded-sm hover:rounded-none",
                                trigger="click",
                                update=button_click,
                            )
                        ],
                        style="flex flex-col",
                    )
                ],
                style="m-auto",
            )
        ],
        style="flex h-screen",
    )

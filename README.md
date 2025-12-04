![Provecta logo](./logo.png)

Provecta is a small, minimal experiment in building an **HTMX + WebSocket-driven UI framework in Python**, written out of both curiosity and JS hate.

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

This creates a lightweight experience as far as the frontend's concerned, because the only job of the browser is to render HTML and orchestrate events.

Minimal Example:

**`app/home.py`**
```python3
def button_click(this: Button, source: Button, root: Root, trigger: str) -> EventResult:
    click_count, set_click_count = this.use_state("click_count", 0)
    set_click_count(click_count + 1)
    this.parent.add(Text(f"this was added on click number {click_count + 1}"))
    return EventResult.MUTATE_PARENT


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

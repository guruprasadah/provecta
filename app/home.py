from element import (
    Button,
    ButtonType,
    Container,
    EventResult,
    Form,
    Image,
    Root,
    Text,
    TextInput,
    TextInputType,
)


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

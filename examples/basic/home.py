from provecta import App, Button, ButtonType, Container, Root, Text


def button_click(this: Button, source: Button, root: Root, trigger: str):
    get_click_count, set_click_count = this.use_state("click_count", 0)
    set_click_count(get_click_count() + 1)
    if get_click_count() + 1 < 10:
        this.parent.add(Text(f"this was added on click number {get_click_count() + 1}"))
    else:
        root.load_into(Root([Text("you clicked the button too many times")]))


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
                style="mt-32 w-64",
            )
        ],
        style="flex h-screen justify-center",
    )

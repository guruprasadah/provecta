from element import Container, EventResult, Image, Root, Text


def text_con_click(this: Container, source: Container, trigger: str) -> EventResult:
    if this == source:
        print("text container was clicked")
        march_count, set_march_count = this.use_state("march_count", 0)
        layout_changed, set_layout_changed = this.use_state("layout_changed", 0)
        if march_count + 1 != 10 or layout_changed:
            set_march_count(march_count + 1)
            this.add(Text(f"march {march_count + 1}"))
            return EventResult.MUTATE_CHILDREN
        else:
            set_layout_changed(True)
            this.style = "flex flex-row"
            return EventResult.MUTATE_SELF
    else:
        return EventResult.NOT_HANDLED


def page() -> Root:
    return Root(
        [
            Container(
                [
                    Image(
                        "https://upload.wikimedia.org/wikipedia/commons/f/fc/Valorant_logo_-_pink_color_version.svg"
                    ),
                    Image(
                        "https://www.theloadout.com/wp-content/sites/theloadout/2022/01/new-valorant-agent-neon.jpg"
                    ),
                    Container(
                        [Text("line 1 of text"), Text("line 2 of text")],
                        style="flex flex-col",
                        update=text_con_click,
                        trigger="click",
                    ),
                ],
                style="flex flex-row h-32 rounded-md border",
            )
        ]
    )

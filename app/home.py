from element import Container, Image, Root, Text


def text_con_click(this: Container, source: Container, trigger: str) -> bool:
    if this == source:
        print("text container was clicked")
        march_count, set_march_count = this.use_state("march_count", 0)
        set_march_count(march_count + 1)
        this.add(Text(f"march {march_count + 1}"))
        return True
    else:
        return False


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

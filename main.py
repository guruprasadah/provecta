from element import Container, Image, Root, Text
from rendering import HTMLRenderer


def text_con_click(this: Container, source: Image, trigger: str):
    (
        this.parent.add(
            Text(
                f"brand image has been clicked for the {this.state.setdefault('click_count', 0)}th time"
            )
        )
    ) if this.parent else None
    print("brand image has been clicked, but event is gonna be bubbled up")
    return True


def main():
    root = Root(
        [
            Container(
                [
                    Image("./brand-image.png"),
                    Image("brand-image-2.png"),
                    Container(
                        [Text("line 1 of text"), Text("line 2 of text")],
                        style="flex flex-col",
                        update=text_con_click,
                        trigger="click",
                    ),
                ],
                style="flex flex-row",
            )
        ]
    )
    r = HTMLRenderer()
    print(r.render(root))


if __name__ == "__main__":
    main()

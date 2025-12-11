from provecta import Container, Root, Text


def page() -> Root:
    return Root(
        [
            Container(
                [
                    Text(
                        "test app within main repo",
                        update=lambda this, y, z, w: this.remove_self(),
                        trigger="click",
                    ),
                    Text(
                        "second line",
                        update=lambda this, y, z, w: this.remove_self(),
                        trigger="click",
                    ),
                    Text(
                        "third line",
                        update=lambda this, y, z, w: this.remove_self(),
                        trigger="click",
                    ),
                    Container(
                        [
                            Text(
                                "fourth line",
                                update=lambda this, y, z, w: this.remove_self(),
                                trigger="click",
                            ),
                            Text(
                                "fifth line",
                                update=lambda this, y, z, w: this.remove_self(),
                                trigger="click",
                            ),
                        ]
                    ),
                ],
                style="flex flex-col space-y-3",
            )
        ]
    )

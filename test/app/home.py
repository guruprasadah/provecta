from provecta import Root, Text


def page() -> Root:
    return Root(
        [
            Text(
                "test app within main repo",
                update=lambda this, y, z, w: this.remove_self(),
                trigger="click",
            )
        ]
    )

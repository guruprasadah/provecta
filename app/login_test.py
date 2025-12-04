import app.punishment
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


def form_submit(this: Form, source: Form, root: Root, trigger: str) -> EventResult:
    if (
        this.fields["email"].value == "guruprasadah08@mail.com"
        and this.fields["password"].value == "hello123"
    ):
        root.load_into(app.punishment.page())

    return EventResult.MUTATE_ALL


f_style_base = (
    "p-2 border transition-colors duration-300 focus:bg-zinc-100 focus:outline-none"
)
f_style_normal = f_style_base + " border-zinc-400"
f_style_invalid = f_style_base + " border-red-500"


def validate_email(
    this: TextInput, source: TextInput, root: Root, trigger: str
) -> EventResult:
    print(f"validating, value: {source.value}")
    if source.value == "guruprasadah08@gmail.com":
        source.style = f_style_invalid
    else:
        source.style = f_style_normal
    return EventResult.MUTATE_SELF


def page() -> Root:
    return Root(
        [
            Container(
                [
                    Form(
                        [
                            TextInput(
                                "email",
                                type=TextInputType.EMAIL,
                                placeholder="Your email",
                                style=f_style_normal,
                                trigger="input changed delay:500ms",
                                update=validate_email,
                            ),
                            TextInput(
                                "password",
                                type=TextInputType.PASSWORD,
                                placeholder="Your password",
                                style=f_style_normal,
                            ),
                            Button(
                                "submit",
                                content="Log in",
                                type=ButtonType.SUBMIT,
                                style="h-8 w-full bg-blue-600 text-white transition-all duration-300 hover:bg-zinc-200 hover:text-black rounded-sm hover:rounded-none",
                            ),
                        ],
                        style="flex flex-col border border-zinc-400 p-4 space-y-2",
                        update=form_submit,
                    )
                ],
                style="m-auto",
            )
        ],
        style="flex h-screen",
    )

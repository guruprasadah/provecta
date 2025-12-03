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


def form_submit(this: Container, source: Container, trigger: str) -> EventResult:
    print("login form submitted")
    return EventResult.NOT_HANDLED


f_style_base = (
    "p-2 border transition-colors duration-300 focus:bg-zinc-100 focus:outline-none"
)
f_style_normal = f_style_base + " border-zinc-400"
f_style_invalid = f_style_base + " border-red-500"


def validate_email(this: TextInput, source: TextInput, trigger: str) -> EventResult:
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
                                "login",
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
                                content="Register",
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

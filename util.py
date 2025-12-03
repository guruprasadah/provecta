import asyncio


def indent(input: str, c=0) -> str:
    return input.replace("\n", "\n" + ("\t" * c))


async def wait_for_either(task_coro, bool_fn, check_interval=0.05):
    loop = asyncio.get_event_loop()
    task = loop.create_task(task_coro)

    async def wait_for_bool():
        while not bool_fn():
            await asyncio.sleep(check_interval)

    bool_task = loop.create_task(wait_for_bool())

    done, pending = await asyncio.wait(
        {task, bool_task}, return_when=asyncio.FIRST_COMPLETED
    )

    # Cancel whichever one is still pointlessly alive
    for p in pending:
        p.cancel()

    # Figure out which completed
    if task in done:
        return ("task", await task)
    else:
        return ("bool", None)

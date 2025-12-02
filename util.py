def indent(input: str, c=0) -> str:
    return input.replace("\n", "\n" + ("\t" * c))

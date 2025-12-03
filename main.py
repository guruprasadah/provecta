from element import Container, TextInput


def main():
    for k, v in Container.__dict__.items():
        if k[0] != "_":
            print(k, v)


if __name__ == "__main__":
    main()

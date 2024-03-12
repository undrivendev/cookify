import typer

import cookify.cookify


def main():
    typer.run(cookify.cookify.run)


if __name__ == "__main__":
    main()

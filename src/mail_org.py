from pathlib import Path

from .map_engine import MapEngine


def main():
    with MapEngine() as me:
        me.apply(Path("mail-org.json"))


if __name__ == '__main__':
    main()

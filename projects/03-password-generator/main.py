"""Print generated passwords locally; no network or file storage is used."""

import argparse
from passwords import DEFAULT_GROUPS, generate_password


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=int, default=16)
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--no-symbols", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.count <= 20:
        parser.error("Count must be 1-20.")
    groups = DEFAULT_GROUPS[:-1] if args.no_symbols else DEFAULT_GROUPS
    try:
        for _ in range(args.count):
            print(generate_password(args.length, groups))
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()

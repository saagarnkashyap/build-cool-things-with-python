"""Launch a friendly terminal number guessing game."""

import argparse
import random
from guessing import play


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--low", type=int, default=1)
    parser.add_argument("--high", type=int, default=100)
    parser.add_argument("--attempts", type=int, default=7)
    parser.add_argument("--seed", type=int, help="Repeat a practice game for demonstrations")
    args = parser.parse_args()
    if args.low > args.high or args.attempts < 1:
        parser.error("Use low <= high and at least one attempt.")
    play(args.low, args.high, args.attempts, rng=random.Random(args.seed))


if __name__ == "__main__":
    main()

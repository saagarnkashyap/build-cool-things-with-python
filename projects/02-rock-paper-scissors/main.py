"""Play a fixed number of rounds, with draws counted and scores shown."""

import argparse
import random
from rps import CHOICES, normalize_choice, round_result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--seed", type=int, help="Repeat a practice match")
    args = parser.parse_args()
    if not 1 <= args.rounds <= 100:
        parser.error("Rounds must be between 1 and 100.")
    rng = random.Random(args.seed)
    score = {"win": 0, "loss": 0, "draw": 0}
    print("Rock, paper, scissors! Type r/p/s, a full word, or q to quit.")
    for number in range(1, args.rounds + 1):
        while True:
            try:
                answer = input(f"Round {number}/{args.rounds}: ").strip()
                if answer.lower() == "q":
                    print("Match ended.")
                    return
                player = normalize_choice(answer)
                break
            except ValueError as exc:
                print(exc)
            except (EOFError, KeyboardInterrupt):
                print("\nMatch ended.")
                return
        computer = rng.choice(CHOICES)
        result = round_result(player, computer)
        score[result] += 1
        print(f"You: {player} | Computer: {computer} | {result.upper()}")
    print(f"Final score: {score['win']} wins, {score['loss']} losses, {score['draw']} draws.")


if __name__ == "__main__":
    main()

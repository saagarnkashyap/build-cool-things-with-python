"""Small, testable rules for the number guessing game."""

import random
from collections.abc import Callable
from dataclasses import dataclass, field


def hint(guess: int, secret: int) -> str:
    if guess < secret:
        return "Too low."
    if guess > secret:
        return "Too high."
    return "Correct!"


@dataclass
class GuessingRound:
    """State for the desktop game, using the same hint rules as the CLI."""

    low: int
    high: int
    limit: int
    secret: int
    guesses: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.low > self.high or self.limit < 1 or not self.low <= self.secret <= self.high:
            raise ValueError("Use an ordered range, positive attempt limit, and a secret inside the range.")

    @property
    def won(self) -> bool:
        return bool(self.guesses) and self.guesses[-1] == self.secret

    @property
    def finished(self) -> bool:
        return self.won or len(self.guesses) >= self.limit

    @property
    def remaining(self) -> int:
        return self.limit - len(self.guesses)

    def submit(self, text: str) -> str:
        if self.finished:
            raise ValueError("This round has ended. Start a new game.")
        try:
            guess = int(text.strip())
        except ValueError:
            raise ValueError("Enter a whole number; no attempt was used.") from None
        if not self.low <= guess <= self.high:
            raise ValueError(f"Choose a number from {self.low} to {self.high}; no attempt was used.")
        self.guesses.append(guess)
        if self.finished and not self.won:
            return f"Out of attempts. The number was {self.secret}."
        return hint(guess, self.secret)


def play(low: int = 1, high: int = 100, attempts: int = 7, *,
         rng: random.Random | None = None, read: Callable = input,
         write: Callable = print) -> bool:
    """Invalid entries do not consume attempts. Return whether the player won."""
    if low > high or attempts < 1:
        raise ValueError("The range must be ordered and attempts must be positive.")
    secret = (rng or random.Random()).randint(low, high)
    write(f"Guess a number from {low} to {high}. You have {attempts} attempts. Enter q to quit.")
    used = 0
    while used < attempts:
        try:
            answer = read(f"Guess {used + 1}/{attempts}: ").strip()
        except (EOFError, KeyboardInterrupt):
            write("\nGame ended.")
            return False
        if answer.lower() == "q":
            write("Game ended.")
            return False
        try:
            guess = int(answer)
        except ValueError:
            write("Please enter a whole number or q.")
            continue
        if not low <= guess <= high:
            write(f"Stay between {low} and {high}; that did not use an attempt.")
            continue
        used += 1
        write(hint(guess, secret))
        if guess == secret:
            write(f"Solved in {used} attempt(s).")
            return True
    write(f"Out of attempts. The number was {secret}.")
    return False

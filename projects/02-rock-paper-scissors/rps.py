"""Rules and scoring for a short match against the computer."""

from dataclasses import dataclass, field

CHOICES = ("rock", "paper", "scissors")
BEATS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}


def normalize_choice(value: str) -> str:
    value = value.strip().lower()
    value = {"r": "rock", "p": "paper", "s": "scissors"}.get(value, value)
    if value not in CHOICES:
        raise ValueError("Choose rock, paper, or scissors (r/p/s).")
    return value


def round_result(player: str, computer: str) -> str:
    player, computer = normalize_choice(player), normalize_choice(computer)
    if player == computer:
        return "draw"
    return "win" if BEATS[player] == computer else "loss"


@dataclass
class Match:
    """Desktop match state; draws count as rounds, just as in the CLI."""

    rounds: int = 5
    history: list[tuple[str, str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not 1 <= self.rounds <= 100:
            raise ValueError("Rounds must be between 1 and 100.")

    @property
    def finished(self) -> bool:
        return len(self.history) >= self.rounds

    @property
    def score(self) -> dict[str, int]:
        return {result: sum(row[2] == result for row in self.history) for result in ("win", "loss", "draw")}

    def play(self, player: str, computer: str) -> str:
        if self.finished:
            raise ValueError("The match has ended. Start a new match.")
        player, computer = normalize_choice(player), normalize_choice(computer)
        result = round_result(player, computer)
        self.history.append((player, computer, result))
        return result

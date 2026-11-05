import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rps import CHOICES, Match, normalize_choice, round_result


class RockPaperScissorsTests(unittest.TestCase):
    def test_all_nine_matchups(self):
        expected = [["draw", "loss", "win"], ["win", "draw", "loss"], ["loss", "win", "draw"]]
        for row, player in enumerate(CHOICES):
            for column, computer in enumerate(CHOICES):
                with self.subTest(player=player, computer=computer):
                    self.assertEqual(round_result(player, computer), expected[row][column])

    def test_shortcuts_and_whitespace(self):
        self.assertEqual(normalize_choice(" R "), "rock")
        self.assertEqual(normalize_choice("SCISSORS"), "scissors")

    def test_invalid_choices(self):
        for value in ("", "lizard", "rr"):
            with self.assertRaises(ValueError):
                normalize_choice(value)

    def test_invalid_computer_choice(self):
        with self.assertRaises(ValueError):
            round_result("rock", "water")


class DesktopMatchTests(unittest.TestCase):
    def test_score_tracks_wins_losses_and_draws(self):
        match = Match(3)
        match.play("r", "scissors")
        match.play("rock", "paper")
        match.play("paper", "paper")
        self.assertEqual(match.score, {"win": 1, "loss": 1, "draw": 1})
        self.assertTrue(match.finished)

    def test_invalid_choice_does_not_add_round(self):
        match = Match()
        with self.assertRaises(ValueError):
            match.play("water", "paper")
        self.assertEqual(match.history, [])

    def test_finished_match_blocks_further_rounds(self):
        match = Match(1)
        match.play("rock", "rock")
        with self.assertRaises(ValueError):
            match.play("paper", "rock")
        self.assertEqual(len(match.history), 1)

    def test_invalid_round_counts(self):
        for count in (0, 101):
            with self.assertRaises(ValueError):
                Match(count)

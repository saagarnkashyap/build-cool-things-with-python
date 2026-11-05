import random
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from guessing import GuessingRound, hint, play


class GuessingTests(unittest.TestCase):
    def test_all_hints(self):
        self.assertEqual(hint(4, 5), "Too low.")
        self.assertEqual(hint(6, 5), "Too high.")
        self.assertEqual(hint(5, 5), "Correct!")

    def test_bad_entries_do_not_consume_attempts(self):
        entries = iter(["oops", "20", "5"])
        output = []
        self.assertTrue(play(5, 5, 1, read=lambda _: next(entries), write=output.append))
        self.assertIn("Solved in 1 attempt(s).", output)

    def test_loss_reveals_number(self):
        output = []
        self.assertFalse(play(1, 10, 1, rng=random.Random(1), read=lambda _: "1", write=output.append))
        self.assertIn("Out of attempts. The number was 3.", output)

    def test_quit_and_eof(self):
        self.assertFalse(play(read=lambda _: "q", write=lambda _: None))
        def ended(_):
            raise EOFError
        self.assertFalse(play(read=ended, write=lambda _: None))

    def test_invalid_setup(self):
        for values in ((10, 1, 3), (1, 10, 0)):
            with self.assertRaises(ValueError):
                play(*values)


class DesktopRoundTests(unittest.TestCase):
    def test_invalid_input_does_not_use_attempts(self):
        game = GuessingRound(1, 10, 3, 5)
        for text in ("hello", "", "0", "11", "3.5"):
            with self.assertRaises(ValueError):
                game.submit(text)
        self.assertEqual(game.remaining, 3)

    def test_hints_and_win_end_the_round(self):
        game = GuessingRound(1, 10, 3, 5)
        self.assertEqual(game.submit("4"), "Too low.")
        self.assertEqual(game.submit("6"), "Too high.")
        self.assertEqual(game.submit(" 5 "), "Correct!")
        self.assertTrue(game.won and game.finished)
        with self.assertRaises(ValueError):
            game.submit("5")
        self.assertEqual(len(game.guesses), 3)

    def test_loss_reveals_secret(self):
        game = GuessingRound(1, 10, 1, 5)
        self.assertEqual(game.submit("2"), "Out of attempts. The number was 5.")
        self.assertTrue(game.finished)
        self.assertFalse(game.won)

    def test_invalid_round_settings(self):
        for arguments in ((10, 1, 3, 5), (1, 10, 0, 5), (1, 10, 3, 11)):
            with self.assertRaises(ValueError):
                GuessingRound(*arguments)

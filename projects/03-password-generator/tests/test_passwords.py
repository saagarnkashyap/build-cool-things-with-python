import string
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from passwords import DEFAULT_GROUPS, generate_password, generate_passwords


class PasswordTests(unittest.TestCase):
    def test_length_and_required_groups(self):
        for length in (4, 16, 128):
            password = generate_password(length)
            self.assertEqual(len(password), length)
            for group in DEFAULT_GROUPS:
                self.assertTrue(any(character in group for character in password))

    def test_custom_alphabet(self):
        password = generate_password(20, (string.digits,))
        self.assertTrue(password.isascii() and password.isdigit())

    def test_no_symbols(self):
        self.assertTrue(generate_password(16, DEFAULT_GROUPS[:-1]).isalnum())

    def test_invalid_lengths(self):
        for length in (0, 3, 129):
            with self.assertRaises(ValueError):
                generate_password(length)

    def test_invalid_groups(self):
        for groups in ((), ("",), ("abc", "")):
            with self.assertRaises(ValueError):
                generate_password(16, groups)

    def test_batches_respect_count_and_selected_groups(self):
        passwords = generate_passwords(20, 3, DEFAULT_GROUPS[:-1])
        self.assertEqual(len(passwords), 3)
        for password in passwords:
            self.assertEqual(len(password), 20)
            self.assertTrue(password.isalnum())
            for group in DEFAULT_GROUPS[:-1]:
                self.assertTrue(any(character in group for character in password))

    def test_invalid_batch_counts(self):
        for count in (0, 21):
            with self.assertRaises(ValueError):
                generate_passwords(16, count)

    def test_batch_rejects_empty_character_selection(self):
        with self.assertRaises(ValueError):
            generate_passwords(16, 2, ())

import unittest
from poet.utils import syllable_counter

class TestSyllableCounter(unittest.TestCase):
    def test_syllable_counts(self):
        self.assertEqual(syllable_counter('syllable'), 3)
        self.assertEqual(syllable_counter('hello'), 2)
        self.assertEqual(syllable_counter('magic'), 2)
        self.assertEqual(syllable_counter('stable'), 2)
        self.assertEqual(syllable_counter('now'), 1)
        self.assertEqual(syllable_counter('i'), 1)
        self.assertEqual(syllable_counter('whatever'), 3)
        self.assertEqual(syllable_counter('absurdity'), 4)
        self.assertEqual(syllable_counter('clone'), 1)
        self.assertEqual(syllable_counter('limitlessness'), 4)
        self.assertEqual(syllable_counter('exaggeration'), 5)

#!/usr/bin/python3

import os
import sqlite3
import unittest

import fts_did_you_mean

class FtsTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")

    def test_fts_similar_words(self):
        """test if similar words are found"""
        with open("sample.txt", "w") as f:
            f.write("""moo
baa
lalala""")
        self.addCleanup(lambda: os.unlink("sample.txt"))
        fts_did_you_mean.create_test_db(self.conn, "sample.txt")
        results = fts_did_you_mean.get_similar_terms_from_db(
            self.conn, "moox")
        self.assertEqual(results, {'moo': 1})

    def test_fts_ranking_raises_on_invalid(self):
        with self.assertRaises(ValueError):
            fts_did_you_mean.get_similar_terms_from_db(
                self.conn, "xx", "mispelled-occurences")

    def test_fts_equal_rank(self):
        """test if similar words are found"""
        with open("sample.txt", "w") as f:
            f.write("""mooa
moob
""")
        self.addCleanup(lambda: os.unlink("sample.txt"))
        fts_did_you_mean.create_test_db(self.conn, "sample.txt")
        results = fts_did_you_mean.get_similar_terms_from_db(
            self.conn, "moox")
        self.assertEqual(results, {'mooa': 1,
                                   'moob': 1})

    def test_fts_ranking(self):
        """Test that the two ranking strategies produce different results"""
        with open("sample.txt", "w") as f:
            f.write("""moo moo
baa
lalala""")
        self.addCleanup(lambda: os.unlink("sample.txt"))
        fts_did_you_mean.create_test_db(self.conn, "sample.txt")
        # we have it twice in the Db
        results = fts_did_you_mean.get_similar_terms_from_db(
            self.conn, "moox", ranking="occurrences")
        self.assertEqual(results, {'moo': 2})
        # but only in one DB record
        results = fts_did_you_mean.get_similar_terms_from_db(
            self.conn, "moox", ranking="documents")
        self.assertEqual(results, {'moo': 1})


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/python3

import os
import sqlite3
import sys
import time


def create_test_db(connection, words="/usr/share/dict/words"):
    """Create a test database with just a bunch of words, note that
       this could be anything (like a product catalog) and also
       note that the "Descr" table could have more text fields
    """
    connection.executescript("""
CREATE VIRTUAL TABLE Descr USING fts4(
       description TEXT);
CREATE VIRTUAL TABLE Description_term USING fts4aux(Descr);
""")
    with open(words) as f:
        for line in f:
            descr = line.strip()
            connection.execute("INSERT INTO Descr VALUES(?);",
                               (descr, ))
    connection.commit()


def similar_words(word):
    """
    return a set with spelling1 distance alternative spellings

    based on http://norvig.com/spell-correct.html
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz-_0123456789'
    s = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in s if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in s if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in s for c in alphabet if b]
    inserts = [a + c + b     for a, b in s for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


def get_similar_terms_from_db(connection, search_term, ranking="documents"):
    """Return similar words for the search terms that are found in the DB
    
    The ranking can either be "documents" or "occurrences"
    """
    if not ranking in ("documents", "occurrences"):
        raise ValueError("ranking must be either 'documents' or 'occurrences'")
    suggestions = {}
    for w in similar_words(search_term):
        # either use "documents" or "occurences" in the query
        #   with "documents" its the number of DB records 
        #   with "occurences" its the number of total occurences 
        #   (even multiple times in the same record)
        cmd = """
SELECT %s FROM Description_term
WHERE Description_term.term = ? and Description_term.col = "*"
""" % ranking
        res = connection.execute(cmd, (w, ))
        data = res.fetchone()
        if data:
            # rank is based on number of "documents" or "occurences" found
            rank = data[0]
            suggestions[w] = rank
    return suggestions


if __name__ == "__main__":
    DB_NAME = "test.db"
    search_term = sys.argv[1]

    if not os.path.exists(DB_NAME):
        connection = sqlite3.connect(DB_NAME)
        create_test_db(connection)
    else:
        connection = sqlite3.connect(DB_NAME)

    now = time.time()
    suggestions = get_similar_terms_from_db(connection, search_term)
    print("Did you mean:")
    for k in sorted(suggestions, key=suggestions.get, reverse=True):
        print(" %s (rank: %s)" % (k, suggestions[k]))
    print("time %s" % (time.time() - now))

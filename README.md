This is a example that implements a "Did you mean 'mistyped-word'?"
using the FTS extension of sqlite3.

The demo will simply use /usr/share/dict/words instead of something
more useful to have some data (initial run takes a bit to build the 
sample DB). But its trivial to hook this into any existing DB that
uses fts already.

Then you can e.g. run:
```
$ ./fts_did_you_mean.py aptx
Did you mean:
 apex (rank: 2)
 apt (rank: 1)
time 0.024138927459716797
```

The tests/test_fts_spell.py has some more example usage.
# etc. and the deny list

`validate.py` rejects `etc.` in every prose field, so an `etc-abbr` entry cannot show its own word in examples. Queue row deferred 2026-10-23. Possible fix: exempt an entry's own headword from the deny list.

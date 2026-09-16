#!/usr/bin/env python3
"""Print the file path, slug, shard, or phrase sub_id for a dictionary entry.

    tools/entry_path.py bank-n                      -> entries/ba/bank-n.json
    tools/entry_path.py --slug "give up" phrv       -> give-up-phrv
    tools/entry_path.py --slug bat n 2              -> bat-n-2
    tools/entry_path.py --shard x-ray-n             -> x
    tools/entry_path.py --sub-id "give someone a hand" -> give-someone-a-hand

The rules are those of wiki/conventions.md section 2, implemented in
tools/eexlib.py.  Exit status 2 with a message on a slug that does not parse
or an unknown part-of-speech code.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eexlib  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Print the path of an entry from its slug, or derive a slug, shard, or phrase sub_id.",
        epilog="With no option, the argument is a slug and the relative path entries/<shard>/<slug>.json is printed.")
    parser.add_argument("--slug", metavar="HEADWORD", help="print the slug of HEADWORD; give the pos code and an optional homograph number after it")
    parser.add_argument("--shard", metavar="SLUG", help="print the shard directory of SLUG")
    parser.add_argument("--sub-id", metavar="TEXT", help="print the sub_id of a phrase")
    parser.add_argument("rest", nargs="*", help="the slug, or with --slug: POS [HOMOGRAPH]")
    args = parser.parse_args(argv)

    try:
        if args.slug is not None:
            if not 1 <= len(args.rest) <= 2:
                parser.error("--slug needs a part-of-speech code and an optional homograph number")
            homograph = args.rest[1] if len(args.rest) == 2 else 1
            print(eexlib.slugify(args.slug, args.rest[0], homograph))
        elif args.shard is not None:
            eexlib.parse_slug(args.shard)
            print(eexlib.shard(args.shard))
        elif args.sub_id is not None:
            print(eexlib.phrase_sub_id(args.sub_id))
        else:
            if len(args.rest) != 1:
                parser.error("give exactly one slug")
            eexlib.parse_slug(args.rest[0])
            print(eexlib.relative_entry_path(args.rest[0]))
    except ValueError as exc:
        print("entry_path: %s" % exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

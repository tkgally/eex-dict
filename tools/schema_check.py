#!/usr/bin/env python3
"""A small JSON-Schema-subset validator for the entry schema (standard library only).

Supported keywords: type (a name or a list; integers are not booleans),
const, enum, properties, required, additionalProperties (false or a schema),
items, minItems, maxItems, minimum, maximum, minLength, maxLength, pattern
(re.search), propertyNames (with pattern), oneOf, anyOf, allOf, $ref to a
local ``#/$defs/...`` or ``#/definitions/...`` target, and the project's own
``x-vocabulary``: a string value must be a key of that vocabulary in
schema/vocabularies.json (keys starting with ``_`` excluded); null passes
only when the type allows null.  Unknown keywords are ignored.

Library use::

    errors = schema_check.validate(instance, schema, vocab)   # [(path, message), ...]

Command line::

    python3 tools/schema_check.py entries/ba/bank-n.json [--schema PATH] [--vocab PATH]

Paths in messages look like ``senses[0].examples[1].text``; the root is ``(root)``.
Exit status 1 when there are errors.
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eexlib  # noqa: E402

_TYPE_NAMES = ("string", "integer", "number", "boolean", "null", "object", "array")


def _type_name(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _has_type(value, name):
    actual = _type_name(value)
    if name == "number":
        return actual in ("integer", "number")
    if name == "integer":
        return actual == "integer" or (actual == "number" and float(value).is_integer())
    return actual == name


def _canon(value):
    """A comparable form that keeps 1, 1.0 and true distinct enough for const/enum."""
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _join(path, key):
    return "%s.%s" % (path, key) if path else str(key)


def _describe(value):
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 60 else text[:57] + "..."


def validate(instance, schema, vocab=None):
    """Validate ``instance`` against ``schema``; return a list of (path, message)."""
    errors = []
    _check(instance, schema, schema, vocab or {}, "", errors)
    return errors


def _check(inst, sch, root, vocab, path, errors):
    if sch is True or sch == {}:
        return
    if sch is False:
        errors.append((path or "(root)", "no value is allowed here"))
        return
    if not isinstance(sch, dict):
        return

    if "$ref" in sch:
        _check(inst, eexlib.resolve_ref(sch["$ref"], root), root, vocab, path, errors)

    types = sch.get("type")
    if types is not None:
        allowed = types if isinstance(types, list) else [types]
        if not any(_has_type(inst, t) for t in allowed):
            errors.append((path or "(root)", "expected type %s, got %s (%s)"
                           % (" or ".join(allowed), _type_name(inst), _describe(inst))))
            return

    if "const" in sch and _canon(inst) != _canon(sch["const"]):
        errors.append((path or "(root)", "must be %s, got %s" % (_describe(sch["const"]), _describe(inst))))
    if "enum" in sch and _canon(inst) not in [_canon(v) for v in sch["enum"]]:
        errors.append((path or "(root)", "%s is not one of %s" % (_describe(inst), _describe(sch["enum"]))))

    if "x-vocabulary" in sch:
        _check_vocabulary(inst, sch, vocab, path, errors)

    if isinstance(inst, str):
        if "minLength" in sch and len(inst) < sch["minLength"]:
            errors.append((path or "(root)", "must be at least %d characters long" % sch["minLength"]))
        if "maxLength" in sch and len(inst) > sch["maxLength"]:
            errors.append((path or "(root)", "must be at most %d characters long" % sch["maxLength"]))
        if "pattern" in sch and not re.search(sch["pattern"], inst):
            errors.append((path or "(root)", "%s does not match pattern %s" % (_describe(inst), sch["pattern"])))

    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in sch and inst < sch["minimum"]:
            errors.append((path or "(root)", "must be at least %s, got %s" % (sch["minimum"], inst)))
        if "maximum" in sch and inst > sch["maximum"]:
            errors.append((path or "(root)", "must be at most %s, got %s" % (sch["maximum"], inst)))

    if isinstance(inst, dict):
        _check_object(inst, sch, root, vocab, path, errors)

    if isinstance(inst, list):
        if "minItems" in sch and len(inst) < sch["minItems"]:
            errors.append((path or "(root)", "must have at least %d items, has %d" % (sch["minItems"], len(inst))))
        if "maxItems" in sch and len(inst) > sch["maxItems"]:
            errors.append((path or "(root)", "must have at most %d items, has %d" % (sch["maxItems"], len(inst))))
        items = sch.get("items")
        if isinstance(items, (dict, bool)):
            for i, item in enumerate(inst):
                _check(item, items, root, vocab, "%s[%d]" % (path, i), errors)

    if "allOf" in sch:
        for branch in sch["allOf"]:
            _check(inst, branch, root, vocab, path, errors)
    if "anyOf" in sch:
        _check_alternatives(inst, sch["anyOf"], "anyOf", root, vocab, path, errors)
    if "oneOf" in sch:
        _check_alternatives(inst, sch["oneOf"], "oneOf", root, vocab, path, errors)


def _check_vocabulary(inst, sch, vocab, path, errors):
    name = sch["x-vocabulary"]
    if inst is None:
        return  # the type keyword decides whether null is allowed
    if not isinstance(inst, str):
        errors.append((path or "(root)", "expected a string from vocabulary %r, got %s" % (name, _type_name(inst))))
        return
    table = vocab.get(name) if isinstance(vocab, dict) else None
    if not isinstance(table, dict):
        errors.append((path or "(root)", "unknown vocabulary %r in the schema" % name))
        return
    if inst.startswith("_") or inst not in table:
        errors.append((path or "(root)", "%s is not a value of vocabulary %r" % (_describe(inst), name)))


def _check_object(inst, sch, root, vocab, path, errors):
    props = sch.get("properties") or {}
    for key in sch.get("required") or []:
        if key not in inst:
            errors.append((path or "(root)", "required key %r is missing" % key))
    for key, value in inst.items():
        if key in props:
            _check(value, props[key], root, vocab, _join(path, key), errors)
    extra = sch.get("additionalProperties", True)
    if extra is not True:
        for key, value in inst.items():
            if key in props:
                continue
            if extra is False:
                errors.append((path or "(root)", "unexpected key %r" % key))
            else:
                _check(value, extra, root, vocab, _join(path, key), errors)
    names = sch.get("propertyNames")
    if isinstance(names, dict) and "pattern" in names:
        for key in inst:
            if not re.search(names["pattern"], key):
                errors.append((path or "(root)", "key %r does not match pattern %s" % (key, names["pattern"])))


def _check_alternatives(inst, branches, keyword, root, vocab, path, errors):
    """oneOf: exactly one branch must match; anyOf: at least one."""
    results = []
    for branch in branches:
        branch_errors = []
        _check(inst, branch, root, vocab, path, branch_errors)
        results.append(branch_errors)
    matching = [i for i, errs in enumerate(results) if not errs]
    if keyword == "anyOf" and matching:
        return
    if keyword == "oneOf" and len(matching) == 1:
        return
    if len(matching) > 1:
        errors.append((path or "(root)", "matches %d of the %s alternatives (%s); exactly one must match"
                       % (len(matching), keyword, ", ".join(str(i + 1) for i in matching))))
        return
    # Nothing matched.  If exactly one branch got past its type check, its
    # errors are the useful ones; otherwise summarize every branch compactly.
    here = path or "(root)"
    typed = [errs for errs in results
             if not (len(errs) == 1 and errs[0][0] == here and errs[0][1].startswith("expected type"))]
    if len(typed) == 1:
        errors.extend(typed[0])
        return
    summary = []
    for i, errs in enumerate(results):
        shown = "; ".join(("%s: %s" % (p, m)) if p != here else m for p, m in errs[:3])
        if len(errs) > 3:
            shown += "; ..."
        summary.append("%d: %s" % (i + 1, shown))
    errors.append((here, "matches none of the %s alternatives (%s)" % (keyword, " | ".join(summary))))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate a JSON file against the entry schema (subset validator, stdlib only).")
    parser.add_argument("file", help="the JSON file to check")
    parser.add_argument("--schema", help="schema file (default: schema/entry.schema.json)")
    parser.add_argument("--vocab", help="vocabularies file (default: schema/vocabularies.json)")
    args = parser.parse_args(argv)

    schema = eexlib.load_json(args.schema) if args.schema else eexlib.load_schema()
    vocab = eexlib.load_json(args.vocab) if args.vocab else eexlib.load_vocab()
    try:
        instance = eexlib.load_json(args.file)
    except (OSError, ValueError) as exc:
        print("%s: cannot read JSON: %s" % (args.file, exc))
        return 1
    errors = validate(instance, schema, vocab)
    for path, message in errors:
        print("%s: %s" % (path, message))
    print("schema_check: %s, %d error%s" % (args.file, len(errors), "" if len(errors) == 1 else "s"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

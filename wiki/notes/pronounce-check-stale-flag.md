# pronounce-check-stale-flag

`tools/pronounce_check.py` appends `pronunciation-disputed` to `provenance.flags` when a transcription comes back `disputed` (line ~285), but never removes it if a later run of the same tool re-verifies the transcription (for example after the drafter fixes the IPA and reruns the check). The flag then sits on a reviewed entry with a fully verified pronunciation.

Caught 2026-09-20 (build run) on `nobody-pron`: the drafted British IPA carried the American stress pattern by mistake, came back `disputed` (1/3 agreement) with the flag added, was corrected by hand, rechecked, came back `verified` (3/3), and the flag had to be removed by hand.

Fix due a later run (about a fifth of a build or lint run at most): after setting `status`, drop `flag` from `flags` when it is present and the new status is not `disputed`.

## 2026-09-20: fixed

`pronounce_check.py` now tracks, per entry, whether any checked variety (American, British) came back `disputed` this run, and syncs `provenance.flags` once after both varieties are checked: the flag is added if any variety is disputed and not already present, and removed if none is disputed and it is present (new helper `update_disputed_flag`, so an entry with one disputed and one verified variety still keeps the flag). Other flags in the list are left untouched. Tests in `tools/tests/test_pronounce_check.py` (`DisputedFlagTests`) cover adding, removing, leaving other flags alone, and idempotence.

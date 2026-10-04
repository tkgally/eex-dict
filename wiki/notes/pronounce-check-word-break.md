# pronounce-check-word-break

*Observed 2026-10-04 (closure cycle, run 20261004T204414Z-sej1s0). [tooling]*

`tools/pronounce_check.py` marked `according-to-prep` **disputed** (American 1/3, British 0/3). Asked again, the panel returned `əˈkɔr.dɪŋ.tə`, `ə.ˈkɔr.dɪŋ.tu`, and `ə.ˈkɔr.dɪŋ.tə`: two of three give the drafter's sounds, but write the break between *according* and *to* as a period, where the style guide (section 11) asks for a space. The comparison treats the space and the period as different, so a multi-word headword can fail on punctuation alone.

Possible fix (a later run, with a logged reason): treat a space and a syllable period as the same boundary in the normalization the agreement rule uses, and add a unit test. Until then, a multi-word headword that comes back disputed is checked by hand against the panel's answers; a separator-only difference gets a curator line, not a change to the transcription.

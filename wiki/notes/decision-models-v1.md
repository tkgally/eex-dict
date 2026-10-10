# Decision models v1: result

*Owner-requested session, 2026-10-10. Code, test sets, per-item verdicts and the full report: [experiments/decision-models-v1](../../experiments/decision-models-v1/report.html). Nothing here changes the pipeline; any adoption is a later, logged decision.*

## What was tested

Decision models answer typed questions about a JSON *state* with probabilities (yes/no, choice, score), bill input tokens only, and return no text; OpenRouter serves them at `POST /api/alpha/decisions` and lists them only under `output_modalities=decisions` (16 distinct models on this date). Eight tasks were built from reviewed entries and `reviews/decisions.jsonl`, with scripted wrong items: pronunciation, definition fit, example to sense, example quality, see-also relevance, link target (homograph), reviewer-issue triage, countability; 1,280 items. A ten-item-per-task screen (pass: 85 percent on the language tasks) kept 13 models. Baselines: GPT-5.6 Terra (reviewer-a, no reasoning), Step 5 Preview, Claude Haiku 5.5, GPT-6 Luna, and the production pronunciation panel.

## Findings

1. On narrow language questions the best decision models match Terra within about two points: example to sense 99 percent (Terra 98), example quality 96 (96), link target 97 (99), see-also 97 (93). They cost US$0.004–0.06 per thousand checks against Terra's US$0.59, at about 0.3 seconds a call against 1.
2. They cannot check IPA (best 69 percent; the panel, which transcribes and compares, scored 100), countability (best 75; Terra 76), or predict an adjudication from the reviewer's note (50–61; chat models 57–69).
3. Real-data pilots. Example to sense over 1,500 real examples: 28 flags, 8 real misfilings, 12 arguable. See-also over all 1,468 links: 100 flags, none clearly wrong; the models cannot see idiom, confusable, or later-sense reasons for a link.
4. Spend: US$3.71, mostly the chat baselines.

## Consequences

- No current paid step is replaced: the two reviewers cover these fields in one whole-entry call.
- Candidate for a later run (owner's call): an advisory example-to-sense flag in review mode, two models agreeing, one line per flag for the adjudicator. Example quality needs a real-data pilot first.

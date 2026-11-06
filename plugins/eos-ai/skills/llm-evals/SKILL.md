---
name: llm-evals
description: Build and run evaluations for LLM features, prompts, agents, and RAG pipelines — golden datasets, assertions, LLM-as-judge graders, regression gates in CI, A/B comparison of prompts or models. Use whenever someone changes a prompt, swaps a model, ships an AI feature, asks "is this better?", "how do I test my agent/chatbot", or reports that an AI feature "sometimes" gives bad answers.
---

# LLM Evals

An eval turns "it seems better" into a number you can track. Without one, every prompt tweak is a coin flip that can silently break cases you fixed last week.

## The minimum viable eval (do this first, ~30 min)

1. **Collect 20–50 real inputs.** Pull from logs, support tickets, or write them by hand to cover: common cases, edge cases (empty, huge, multilingual, adversarial/prompt-injection), and every bug you've already fixed.
2. **Write the expected behavior per case** — not necessarily an exact answer; often a set of checks.
3. **Grade with the cheapest reliable method:**
   - Code checks first: valid JSON/schema, contains/doesn't contain, regex, exact match on a field, length bounds, tool X was called with arg Y, latency < N.
   - LLM-as-judge only for genuinely fuzzy criteria (tone, faithfulness to source, helpfulness). Give the judge a rubric with a binary or 1–3 scale per criterion, ask for reasoning before the verdict, and spot-check ~10% of judge verdicts by hand.
4. **Run it, save results** (`evals/results/<date>-<prompt_version>.jsonl`) with input, output, per-check pass/fail, model, tokens, latency.
5. **Report**: overall pass rate, per-category pass rate, and the actual failing outputs. Read the failures — that's where the insight is.

## File layout (adapt to the project)

```
evals/
  cases.jsonl          # {"id", "input", "checks": [...], "tags": [...]}
  graders.py|ts        # code checks + judge prompt
  run.py|ts            # runs cases concurrently, writes results
  results/             # timestamped outputs (gitignore large ones)
```

Use the project's language. If the project already uses promptfoo, inspect-ai, braintrust, langsmith, or the Claude Console eval tool, use that instead of rolling your own.

## Comparing versions

- Run baseline and candidate on the **same** cases, same model settings. Report the delta and list cases that flipped pass→fail (regressions) separately from fail→pass.
- LLM outputs vary: run each case 3× for anything near the threshold and report mean ± spread.
- For subjective quality, do a blind pairwise comparison (judge sees A/B in random order).

## Regression gate

Add the eval to CI (or a pre-merge script) for prompt/model changes with a threshold: fail if pass rate drops > X points or any case tagged `critical` fails. Keep the gate fast — a small critical subset on every change, the full set nightly.

## Agents

Grade the trajectory, not only the final answer: right tools called, no forbidden tools, number of turns, cost, and whether it stopped correctly. Record full transcripts.

## RAG

Separate retrieval evals (did the right chunk appear in top-k? recall@k, MRR) from generation evals (is the answer faithful to the retrieved context and does it cite it?).

## Anti-patterns

- Testing only the happy-path demo prompt.
- Judge with no rubric ("is this good?") → noise.
- Changing cases and prompt at the same time → you can't attribute the change.
- Treating a 2-point move on 20 cases as signal.

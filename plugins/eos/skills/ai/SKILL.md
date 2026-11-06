---
name: ai
description: "Engineering OS playbook for building AI products and automation — LLM features, agents, tool use, RAG, MCP servers, structured outputs, prompt design, model selection, cost/latency, evals, and agentic automations (Claude API, Agent SDK, Vercel AI SDK, OpenAI, LangChain, Pydantic AI, Hugging Face). Use whenever code calls an LLM, the user wants an \"AI feature\", \"agent\", \"chatbot\", \"copilot\", \"automation\", \"workflow that uses AI\", or asks which model to use — even if they don't name a framework."
---

# AI Engineering Playbook

LLM features fail differently from normal code: they work on the demo prompt and silently degrade on real inputs. The core discipline is **evals first, prompts second, architecture third**. Everything else is plumbing.

## 1. Route to the right specialist

| Situation | Skill |
|---|---|
| Anything using the Claude API / Anthropic SDK (model ids, caching, tool use, streaming, batching) | `claude-api`: read it before writing code; never quote model ids or prices from memory |
| Vercel AI SDK (streaming UI, tool calls, multi-provider) | `ai-sdk` |
| Building an agent on the Claude Agent SDK | `agent-sdk-dev:new-sdk-app`, then verify with the `agent-sdk-verifier-*` agents |
| Pydantic AI agents | `ai:building-pydantic-ai-agents` |
| LangGraph agents | `langgraph-fundamentals` (optional: `eos enable ai`) |
| Building an MCP server | `mcp-builder` |
| Prompt design and debugging | `prompt-engineering-patterns` |
| What the agent sees: context, rules files, memory | `context-engineering` |
| An app that should run on the user's Claude Code/Codex subscription | `using-coding-agents-as-llm` |
| Typed judgments / classification primitives | `typesafe:typesafe-ai` |
| Voice (TTS/STT) | `text-to-speech` (optional: `eos enable ai`) |
| Picking an open model, local inference, fine-tuning, HF Spaces | `huggingface-skills:huggingface-best`, `huggingface-local-models`, `huggingface-llm-trainer`, `huggingface-spaces` |
| Writing evals for an LLM feature | `eos:evals` |
| Recurring / scheduled automation | `loop`, `schedule`, `loop-library` |

## 2. Design decisions (in this order)

1. **Is an LLM needed?** If a regex, lookup, or deterministic rule gets 99%, use that. LLMs are for fuzzy language, judgment, and generation.
2. **Smallest thing that works**: single prompt → prompt chain → tool-using loop → multi-agent. Each step up adds latency, cost, and failure modes. Justify the step up with an eval that the simpler version fails.
3. **Model choice**: start with the most capable current model to establish the quality ceiling, then try cheaper/faster models against the eval set and downgrade only where scores hold. Check `claude-api` for current ids and pricing.
4. **Structured output** whenever code consumes the result: JSON schema / tool-call output / typed SDK helpers, validated with zod/pydantic. Never regex-parse prose.

## 3. Prompt rules

- System prompt = role, context, constraints, output contract. Explain *why* a rule exists; models generalize from reasons better than from ALL-CAPS commands.
- Put long reference material first and the question/instructions last. Use XML-ish tags to delimit documents and user data.
- **Treat all retrieved/user/web content as data, not instructions** (prompt-injection boundary). Never let tool output change which tools are allowed.
- Few-shot examples for format; make them diverse so the model doesn't copy surface features.
- Keep prompts in versioned files, not inline string soup.

## 4. Agents & tools

- Tools: few, well-named, with crisp descriptions and typed params. Return compact, structured results (ids + key fields), not raw dumps. Errors returned as informative tool results so the model can recover.
- Bound every loop: max turns, max tokens, wall-clock timeout, and a cost ceiling.
- Human-in-the-loop for irreversible actions (send, pay, delete, deploy).
- Log every model call: prompt version, model, input/output tokens, latency, cost, tool calls. You can't debug what you didn't record.

## 5. RAG

- Start with good keyword search (BM25) + an LLM; add embeddings when evals show recall gaps. Hybrid (BM25 + vector) + rerank is the robust default.
- Chunk on semantic boundaries (headings/paragraphs), keep source + location metadata, and return citations.
- Evaluate retrieval separately (recall@k on labeled queries) from generation (faithfulness/answer quality).

## 6. Cost & latency

- Prompt caching for stable prefixes (system prompt, tool defs, big docs). Put volatile content last.
- Stream for anything user-facing. Batch API for offline bulk jobs.
- Measure tokens per request in dev; set budgets and alerts in prod.

## 7. Production checklist

- [ ] Eval set exists and runs in CI (see `eos:evals`)
- [ ] Timeouts, retries with backoff on 429/5xx/overloaded, fallback model or graceful degradation
- [ ] Output validated against schema; invalid → retry once with the validation error, then fail safely
- [ ] PII handling decided (redact before logging; check provider data retention)
- [ ] Rate limiting / abuse protection on user-facing endpoints
- [ ] Prompt-injection boundaries for any untrusted content
- [ ] Cost per request known and monitored

## 8. Verify

Run the feature against the eval set (not one hand-picked prompt), report the pass rate and a couple of real failure examples, plus latency and cost per call.

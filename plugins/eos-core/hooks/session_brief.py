#!/usr/bin/env python3
"""SessionStart: detect the project's stack and tell Claude which Engineering OS playbooks apply.

Kept deliberately short (a few lines of context) because it runs on every session.
Stdout of a SessionStart hook is added to Claude's context.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _eos import read_input  # noqa: E402

JS_SIGNALS = {
    "next": ("Next.js", "frontend"), "react": ("React", "frontend"), "vue": ("Vue", "frontend"),
    "svelte": ("Svelte", "frontend"), "@sveltejs/kit": ("SvelteKit", "frontend"), "astro": ("Astro", "frontend"),
    "vite": ("Vite", "frontend"), "tailwindcss": ("Tailwind", "frontend"), "react-native": ("React Native", "frontend"),
    "expo": ("Expo", "frontend"), "three": ("three.js", "frontend"),
    "express": ("Express", "backend"), "fastify": ("Fastify", "backend"), "hono": ("Hono", "backend"),
    "@nestjs/core": ("NestJS", "backend"), "prisma": ("Prisma", "backend"), "@prisma/client": ("Prisma", "backend"),
    "drizzle-orm": ("Drizzle", "backend"), "@supabase/supabase-js": ("Supabase", "backend"),
    "better-auth": ("Better Auth", "backend"), "stripe": ("Stripe", "backend"), "trpc": ("tRPC", "backend"),
    "@anthropic-ai/sdk": ("Anthropic SDK", "ai"), "@anthropic-ai/claude-agent-sdk": ("Claude Agent SDK", "ai"),
    "openai": ("OpenAI SDK", "ai"), "ai": ("Vercel AI SDK", "ai"), "langchain": ("LangChain", "ai"),
    "@langchain/core": ("LangChain", "ai"), "@modelcontextprotocol/sdk": ("MCP", "ai"), "@mastra/core": ("Mastra", "ai"),
    "playwright": ("Playwright", "frontend"), "@playwright/test": ("Playwright", "frontend"),
}
PY_SIGNALS = {
    "fastapi": ("FastAPI", "backend"), "django": ("Django", "backend"), "flask": ("Flask", "backend"),
    "sqlalchemy": ("SQLAlchemy", "backend"), "anthropic": ("Anthropic SDK", "ai"), "openai": ("OpenAI SDK", "ai"),
    "langchain": ("LangChain", "ai"), "pydantic-ai": ("Pydantic AI", "ai"), "pydantic_ai": ("Pydantic AI", "ai"),
    "claude-agent-sdk": ("Claude Agent SDK", "ai"), "transformers": ("Transformers", "ai"), "torch": ("PyTorch", "ai"),
    "mcp": ("MCP", "ai"), "gradio": ("Gradio", "ai"), "scrapy": ("Scrapy", "research"), "playwright": ("Playwright", "frontend"),
}
FILE_SIGNALS = {
    "go.mod": ("Go", "backend"), "Cargo.toml": ("Rust", "backend"), "Gemfile": ("Ruby", "backend"),
    "Dockerfile": ("Docker", "backend"), "docker-compose.yml": ("Docker Compose", "backend"),
    "compose.yaml": ("Docker Compose", "backend"), "supabase": ("Supabase", "backend"),
    "Package.swift": ("Swift", "frontend"), "shopify.theme.toml": ("Shopify theme", "frontend"),
    "wrangler.toml": ("Cloudflare Workers", "backend"), "vercel.json": ("Vercel", "frontend"),
}

PLAYBOOKS = {
    "frontend": "eos-frontend:frontend-playbook",
    "backend": "eos-backend:backend-playbook",
    "ai": "eos-ai:ai-engineering",
    "research": "eos-research:research",
}


def read_text(path, limit=200_000):
    try:
        with open(path, errors="ignore") as f:
            return f.read(limit)
    except Exception:
        return ""


def detect(root):
    found, domains = [], set()

    def add(label, domain):
        if label not in found:
            found.append(label)
        domains.add(domain)

    pkg = os.path.join(root, "package.json")
    if os.path.isfile(pkg):
        try:
            d = json.loads(read_text(pkg))
            deps = {**d.get("dependencies", {}), **d.get("devDependencies", {})}
            for k, (label, dom) in JS_SIGNALS.items():
                if k in deps:
                    add(label, dom)
            if "typescript" in deps:
                found.insert(0, "TypeScript")
        except Exception:
            pass
    py = (read_text(os.path.join(root, "pyproject.toml")) + read_text(os.path.join(root, "requirements.txt"))).lower()
    if py:
        found.append("Python")
        for k, (label, dom) in PY_SIGNALS.items():
            if k in py:
                add(label, dom)
    for f, (label, dom) in FILE_SIGNALS.items():
        if os.path.exists(os.path.join(root, f)):
            add(label, dom)
    return found, domains


def main():
    data = read_input()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
    found, domains = detect(root)
    is_git = os.path.isdir(os.path.join(root, ".git"))
    has_claude_md = os.path.isfile(os.path.join(root, "CLAUDE.md"))

    lines = ["[Engineering OS] active."]
    if found:
        lines.append("Stack detected: " + ", ".join(dict.fromkeys(found)) + ".")
        books = [PLAYBOOKS[d] for d in ("frontend", "backend", "ai", "research") if d in domains]
        if books:
            lines.append("Relevant playbooks (load before domain work): " + ", ".join(books) + ".")
    else:
        lines.append("No project stack detected (not a code repo, or a new one).")
    lines.append("Route any task through the `eos-core:eos` skill map when unsure which skill fits. "
                 "Non-code domains: eos-gtm:gtm-strategy, eos-research:research, eos-reverse-engineering:reverse-engineering.")
    if is_git and not has_claude_md:
        lines.append("This repo has no CLAUDE.md; offer to create one (/init) if the user will work here repeatedly.")
    print(" ".join(lines))
    sys.exit(0)


if __name__ == "__main__":
    main()

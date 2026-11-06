#!/usr/bin/env python3
"""SessionStart: detect the project's stack and tell Claude which Engineering OS playbooks apply.

Kept deliberately short (a few lines of context) because it runs on every session.
Stdout of a SessionStart hook is added to Claude's context.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _eos import eos_home, read_input, update_notice  # noqa: E402

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
    "@langchain/core": ("LangChain", "ai"), "@modelcontextprotocol/sdk": ("MCP", "ai"), "@mastra/core": ("Mastra", "ai"), "convex": ("Convex", "backend"),
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
    "frontend": "eos:frontend",
    "backend": "eos:backend",
    "ai": "eos:ai",
    "research": "eos:research",
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


def pack_nudge(found):
    """If the stack matches a domain whose optional (stack-specific) skills aren't installed, suggest `eos enable`."""
    home = eos_home()
    if not home or not found:
        return ""
    try:
        reg = json.load(open(os.path.join(home, "registry", "community.json")))
    except Exception:
        return ""
    skills_dir = os.path.join(os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude"), "skills")
    for dom, spec in reg.get("domains", {}).items():
        hits = [s for s in spec.get("signals", []) if s in found]
        missing = [e.split("@", 1)[1] for e in spec.get("optional", []) if not os.path.isdir(os.path.join(skills_dir, e.split("@", 1)[1]))]
        if hits and missing:
            return (f"This project uses {', '.join(hits)}; official skills for it are available but not installed. "
                    f"Suggest the user run `eos enable {dom}` once.")
    return ""


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
    lines.append("Route any task through the `eos:map` skill map when unsure which skill fits. "
                 "Non-code domains: eos:gtm, eos:research, eos:reverse.")
    home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    try:
        rules_on = "engineering-os" in open(os.path.join(home, "CLAUDE.md")).read()
    except Exception:
        rules_on = False
    if not rules_on:
        lines.append("Engineering OS setup is incomplete on this machine (no global rules / community skills): "
                     "suggest the user run /eos:setup once.")
    nudge = pack_nudge(found)
    if nudge:
        lines.append(nudge)
    if is_git and not has_claude_md:
        lines.append("This repo has no CLAUDE.md; offer to create one (/init) if the user will work here repeatedly.")
    out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": " ".join(lines)}}
    upd = update_notice()
    if upd:
        out["systemMessage"] = upd[0]
        out["hookSpecificOutput"]["additionalContext"] += " " + upd[1]
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()

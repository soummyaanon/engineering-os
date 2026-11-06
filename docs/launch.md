# Launch kit

Ready-to-post copy. Attach `site/og.png` (or a 20–30s screen recording of the install page's terminal demo) to every post. Links: https://engineering-os-hazel.vercel.app · https://github.com/soummyaanon/engineering-os

Best order: X thread → Show HN the next weekday morning (US Eastern ~8–10am) → Reddit the same day → LinkedIn → Product Hunt once you have a few stars and replies to point to. Reply to every comment in the first two hours.

## X / Twitter thread

1/
I set up my coding agent the way a senior engineer would set up a new teammate: the right playbooks, the best skills from the people who build the tools, and guardrails for the expensive mistakes.

Then I made it one command. Engineering OS 👇

2/
`curl -fsSL https://engineering-os-hazel.vercel.app/install | bash`

Works with Claude Code, Codex, Cursor, Gemini CLI, Copilot, Windsurf and 70+ other agents.

3/
What's inside:
• 9 playbooks: /eos:frontend /eos:backend /eos:ai /eos:evals /eos:reverse /eos:research /eos:gtm
• 115 vetted skills (Vercel, Supabase, Prisma, Anthropic, GSAP, shadcn, ui-ux-pro-max…)
• /eos:map tells the agent which skill fits the task

4/
The guard hooks are my favourite part. Even in auto mode:
• `rm -rf ~` never runs
• force-push, push to main, reset --hard, DROP TABLE, curl | sh, prod deploys ask first
• real API keys don't get written into source

5/
It's stack-aware. Open a Next.js + Prisma repo and the agent is pointed at the right playbook. Open an Expo app and it suggests the mobile pack.

6/
It grows with you. `/eos:add stripe webhooks` searches the open skills directory, keeps only reputable sources, and records the pick so every machine gets it.

7/
Free, MIT, and the installer is under 80 lines you can read first.
⭐ https://github.com/soummyaanon/engineering-os

## Show HN

**Title:** Show HN: Engineering OS – one command to give any coding agent vetted skills and guardrails

**Body:**
I kept re-explaining the same things to Claude Code in every repo: how we verify UI, which Postgres rules matter, don't force-push, don't commit keys. Skills exist for most of this, but there are thousands of them and agents rarely pick the right one.

Engineering OS is my attempt at a curated harness:

- 9 playbooks (frontend, backend, AI, evals, reverse engineering, research, GTM) that route to the right specialist skills
- 115 community skills from vendors and well-known authors (Vercel, Supabase, Prisma, Anthropic, GSAP, shadcn, Addy Osmani, Corey Haines…), only 65 installed by default to keep the agent's choices sharp
- Hooks for Claude Code: a bash guard (blocks rm -rf ~, asks before force-push / DROP TABLE / curl | sh / prod deploys), a secret guard, stack detection, and update notices
- Works for 70+ agents through the open skills format (Claude Code gets the hooks too)

Install: `curl -fsSL https://engineering-os-hazel.vercel.app/install | bash` (or read install.sh first, it's short). There's also a prompt you can paste into any agent so it installs itself.

I'd love feedback on the skill picks, especially areas where you know a better skill than the one I chose.

## Reddit (r/ClaudeAI, r/ChatGPTCoding, r/cursor)

**Title:** I packaged my coding-agent setup into one command: 115 vetted skills, playbooks and safety guards (Claude Code, Codex, Cursor, 70+ agents)

**Body:** Same as Show HN, shortened to the bullets. Lead with the guard hooks screenshot on r/ClaudeAI; lead with "works in Cursor/Codex too" on the others. Follow each sub's self-promo rules.

## LinkedIn

Coding agents are only as good as the setup around them.

I packaged mine into Engineering OS: 9 playbooks, 115 vetted skills from the teams behind Vercel, Supabase, Prisma, Anthropic and GSAP, and guardrails that stop an agent from force-pushing to main or committing an API key, even in auto mode.

One command installs it for Claude Code, Codex, Cursor and 70+ other agents. Free and open source.

https://engineering-os-hazel.vercel.app

## Product Hunt

- **Name:** Engineering OS
- **Tagline (60):** One command to give any coding agent senior-engineer habits
- **Description:** Engineering OS installs curated playbooks, 115 vetted skills and safety guards into Claude Code, Codex, Cursor and 70+ coding agents. Stack-aware, self-updating, open source.
- **First comment:** the Show HN body, plus a GIF of the terminal demo.

## Checklist before posting

- [ ] Upload `site/og.png` as the GitHub social preview (repo Settings → General → Social preview); GitHub has no API for this
- [ ] Pin the repo on your GitHub profile
- [ ] Record a 20–30s GIF of the install page demo for the X thread
- [ ] Make sure `eos update` and the install command work on a clean machine the morning of the launch

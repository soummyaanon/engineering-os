#!/usr/bin/env python3
"""Share links printed by eos score / eos redteam must parse on the site, with the same numbers.

Runs the real CLI (--json) on an empty setup and on one with the eos guards, then feeds each share_url's code to the
site's own parser (site/api/_share.js) under node. Run: python3 tests/test_share_links.py (needs node).
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCORE = os.path.join(ROOT, "bin", "eos_score.py")
PARSER = "file://" + os.path.abspath(os.path.join(ROOT, "site", "api", "_share.js"))
SITE = "https://engineering-os-hazel.vercel.app"
CATS = ["Guardrails", "Working rules", "Skills", "Feedback loops"]

NODE = """
import { parseScore, parseRedteam } from %s;
const [kind, code] = process.argv.slice(1);
console.log(JSON.stringify(kind === "s" ? parseScore(code) : parseRedteam(code)));
""" % json.dumps(PARSER)


def cli(config_dir, *args):
    env = {**os.environ, "CLAUDE_CONFIG_DIR": config_dir}
    out = subprocess.run([sys.executable, SCORE, *args, "--json", "--project", tempfile.gettempdir()],
                         env=env, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def parse(url):
    kind, code = url.removeprefix(SITE + "/").split("/", 1)
    out = subprocess.run(["node", "--input-type=module", "-e", NODE, kind, code],
                         capture_output=True, text=True, check=True).stdout
    return kind, json.loads(out)


def check_score(name, d):
    kind, p = parse(d["share_url"])
    assert kind == "s" and p, f"{name}: site rejected {d['share_url']}"
    assert (p["score"], p["grade"]) == (d["score"], d["grade"]), (name, p, d)
    assert [c["pct"] for c in p["cats"]] == [d["categories"][c] for c in CATS], (name, p["cats"], d["categories"])
    rt = d["redteam"]
    want = {"stopped": rt["stopped"], "attacks": rt["attacks"], "falseAlarms": rt["false_alarms"]} if rt else None
    assert p["rt"] == want, (name, p["rt"], want)
    print(f"ok: {name} score -> {d['share_url']}")


def check_redteam(name, d):
    kind, p = parse(d["share_url"])
    assert kind == "r" and p, f"{name}: site rejected {d['share_url']}"
    assert (p["stopped"], p["attacks"], p["falseAlarms"], p["everyday"]) == \
        (d["stopped"], d["attacks"], d["false_alarms"], d["everyday"]), (name, p, d)
    assert [(c["name"], c["stopped"], c["total"]) for c in p["cats"]] == \
        [(k, v["stopped"], v["total"]) for k, v in d["by_category"].items()], (name, p["cats"], d["by_category"])
    print(f"ok: {name} redteam -> {d['share_url']}")


with tempfile.TemporaryDirectory() as empty, tempfile.TemporaryDirectory() as guarded:
    os.makedirs(os.path.join(guarded, "skills"))
    os.symlink(os.path.abspath(os.path.join(ROOT, "plugins", "eos")), os.path.join(guarded, "skills", "eos"))
    for name, cfg in (("empty setup", empty), ("eos guards", guarded)):
        check_score(name, cli(cfg))
        check_redteam(name, cli(cfg, "redteam"))
    check_score("no redteam", cli(empty, "--no-redteam"))
print("share links: all checks passed")

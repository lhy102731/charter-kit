# DSH target

This directory is the DSH adapter source for Charter Kit. The generated,
self-contained DSH plugin lives at `plugins/dsh-charter-kit/`. This target is
not directly loadable: `main` names `lib/index.js`, which the builder emits into
the distribution, and the `./client` export names the `client/client.js` the
builder places there — the pattern `main` already followed — so load the built
plugin, not this directory.

Build the DSH distribution from the repository root:

```text
python scripts/build_dsh_plugin.py
```

The built plugin registers the `charter-workflow` skill. It deliberately
does NOT register a handler-style `/charter-workflow` slash command, so a
typed line such as `/charter-workflow <requirement>` reaches the model as an
ordinary user message — the model loads the skill and starts, resumes, or
runs change triage exactly like the Codex target. It does not install or
download superpowers / j-space / grill-me.

The plugin also registers the Host settings namespace `charter-kit-review` and
the `charter_review` tool. The namespace keys a card in the DSH
plugin-configuration page where Review A and Review B each pick a configured
model, an unset pick follows the session model, and a numeric field sets the
per-review timeout in seconds (default 600, clamped by the tool to 30–1800 s).
That value is the budget for ONE ATTEMPT, not for the whole call: a review makes
at most two attempts — the configured route, then the session model — and an
attempt that outruns its budget is aborted. A genuinely silent provider stream is
cut by the Host's own PER-STREAM IDLE watchdog, which bounds silence rather than
duration; this value neither replaces that mechanism nor is sized against it, and
what it does bound is our own patience. At the 1800 s maximum, two attempts can
hold the reviewer seat for about an hour, so that setting should be deliberate.
All three bounds are provisional: 270 s was measured and found too small (a real
project's Review B lost two attempts to this tool's own clock, with one seat
needing 130 s for a compact brief and the other spending 85 s and 5 702 reasoning
tokens on a single completion), so the replacement errs high on purpose, and the
calibration in `docs/superpowers/calibration/` is what replaces these numbers.
The declared `timeoutMs` is derived in code from those constants — two attempts
at the maximum, plus the margin — so raising the maximum without re-deriving it
fails a test rather than shipping a deadline the Host can preempt. The tool runs
one context-free
review with the configured
model and reports the route it used, or `inherited` when it followed the session
model. Every way the configured route fails to produce a review — a failed
child, an empty result, or that timeout, which makes the tool abort the child —
is handled the same way: the SAME brief is rerun on the session model in a
fresh, context-free child, the result is `outcome: "fallback"`, and
`routeFallbackReason` names the route, what happened, and how long it took. That
fallback still produces a review on the session model, so a configured route that
cannot deliver does not cost the leaf its review. Hence the brief has to be
SELF-CONTAINED — a self-contained brief carrying the candidate diff — because a
review is a MULTI-TURN agent
run — the child reads files, runs `git diff`, then writes — so turns multiplied by
tokens is the whole cost, and a child that must discover the diff itself pays for
that discovery in turns. For the same reason a slow seat belongs on a narrow,
risk-triggered review rather than on every leaf. Dispatch, the child's result,
and teardown are each raced against the attempt's deadline, so a provider that
never publishes a run or never releases one cannot hold the call open. An empty
`review` is never returned as a success shape — it comes back only
as an explicit `outcome: "unavailable"` carrying a reason. That is what happens
when no reviewer could be started at all (no calling agent, or no unambiguous
subagent provider), when the session-model attempt itself failed, or when the
configured route failed and the rerun failed too; there is genuinely no review to
report in each of those cases. An
optional `route: "session"` argument skips the configured route and runs the
session model directly, which is how later reviews of a `(kind, route)` that
already failed in this session avoid re-paying the timeout. A missing
`charter_review` tool or an unused route is not a loss of review independence:
independence and model routing are recorded separately.

## Reasoning-effort selection

Below the two model rows the card carries a 思考强度 (reasoning-effort) area:
one single-choice panel per seat, eight cells in two columns, in the same order
the reference editor renders them — off / low / high / max down the left column,
minimal / medium / xhigh down the right, with the last row's right cell empty.
Each row's value column is read-only text showing what the copied knowledge base
resolves for that model, and 自动适配 fills those values from the table and
selects the table's default level when the model declares it.

Which levels can be picked follows the model's OWN declaration — the model
catalog's `reasoning.efforts` — because that is the set the LLM layer checks a
request against: any other id comes back as `UNSUPPORTED_REASONING_EFFORT`, so a
level the route does not declare is greyed out with the reason beside it. Where
the table and the model disagree, the panel prints both and says that the model
declaration is the one it trusts. The selection is what the tool sends as
`agentOptions.reasoningEffort` — the level ID, not the table's provider wire
string; the wire string is a property of the model's configuration, which this
card displays and does not edit. The table itself is copied data:
`client/effort-knowledge.js` carries it with the upstream name, version, URL,
licence and the extraction command in its header, and the same regions are
embedded in `client/client.js` because the shell's client module table cannot
load a sibling file — `tests/test_dsh_effort_knowledge.py` compares the two byte
for byte. Upstream is dsh-better-reasoning-effort 0.3.9 (MIT); the full upstream
licence text is reproduced under "Third-party notices" in `LICENSE`.

The tool result reports `effort` beside `model`: the level id when one was sent,
`"default"` when none was, meaning the provider default applies and this Host
cannot know which level that is. No level is ever guessed, and when the Host has
no `llm` service to check a route against — that service waits in its own
optional scope precisely so its absence degrades the report instead of taking
the tool down — the result carries no `effort` field at all.

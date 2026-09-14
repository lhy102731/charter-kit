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
per-review timeout in seconds (default 240, clamped by the tool to 30–270 s).
That range is dimensioned against the whole call, not one attempt: a configured
attempt plus a session-model rerun is at most 2 × 270 + 30 = 570 s, still below
the Host's ~600 s external ceiling, so the tool returns its own result before
that ceiling instead of being preempted by it. The tool runs one context-free
review with the configured
model and reports the route it used, or `inherited` when it followed the session
model. Every way the configured route fails to produce a review — a failed
child, an empty result, or that timeout, which makes the tool abort the child —
is handled the same way: the same brief is rerun on the session model in a
fresh, context-free child, the result is `outcome: "fallback"`, and
`routeFallbackReason` names the route, what happened, and how long it took. The
call never waits past its budget and never hands back an empty review. An
optional `route: "session"` argument skips the configured route and runs the
session model directly, which is how later reviews of a `(kind, route)` that
already failed in this session avoid re-paying the timeout. A missing
`charter_review` tool or an unused route is not a loss of review independence:
independence and model routing are recorded separately.

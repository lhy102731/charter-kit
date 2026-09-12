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
model; an unset pick follows the session model. The tool runs one context-free
review with the configured model and reports the model that actually ran. When
a configured route is unavailable the tool still reviews on the session model
and names the route it could not use in `routeFallbackReason`. A missing
`charter_review` tool or an unused route is not a loss of review independence:
independence and model routing are recorded separately.

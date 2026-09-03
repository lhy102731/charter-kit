# DSH target

This directory is the DSH adapter source for Charter Kit. The generated,
self-contained DSH plugin lives at `plugins/dsh-charter-kit/`.

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
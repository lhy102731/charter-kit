# DSH target

This directory is the DSH adapter source for Charter Kit. The generated,
self-contained DSH plugin lives at `plugins/dsh-charter-kit/`.

Build the DSH distribution from the repository root:

```text
python scripts/build_dsh_plugin.py
```

The built plugin registers the `charter-workflow` skill and the
`/charter-workflow` command. It supports starting, resuming, and change
triage for the Charter Kit workflow. It does not install or download
superpowers / j-space / grill-me.
# DSH target

This directory is an **experimental / unverified** DSH adapter source for
Charter Kit. Codex is the only target currently verified for installation and
startup. The generated, self-contained DSH package at
`plugins/dsh-charter-kit/` is retained for adapter development and is not a
supported-install release.

Build the DSH distribution from the repository root:

```text
python scripts/build_dsh_plugin.py
```

The build output is subject to structural checks only. A real DSH host smoke
test and a separate release decision are required before any installation
guidance can be published. Building this adapter does not install or download
superpowers / j-space / grill-me, and it does not install a Harness.

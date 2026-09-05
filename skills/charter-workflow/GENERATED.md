# Generated tree - do not hand-edit

`skills/charter-workflow/` is produced by `python scripts/build_codex_plugin.py`. Every build replaces
this tree, so an edit made here is deleted rather than merged, and nothing
reports the loss.

Edit `targets/codex/skills/charter-workflow/` instead, then regenerate:

```text
python scripts/build_codex_plugin.py
```

The same command writes this tree back after it builds `plugins/charter-kit/`, and it also generates the root `.codex-plugin/plugin.json`. `python scripts/build_dsh_plugin.py` reads this tree as its Skill input, so run the Codex builder first.

`docs/MIRROR-TOPOLOGY.md` maps every copy in this repository to the tree an
edit survives in.

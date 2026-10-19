#!/usr/bin/env python
"""Charter Kit governance self-checks: the single implementation of every acceptance item.

Each acceptance item in .charter/current-task.md names one of these checks by id. The check
body lives here and nowhere else, so one rule has one implementation and there is no second
copy to drift (REV-CHARTER-20 main verdict: point-fixes left the same rule implemented twice).

Usage:
  python .charter/checks.py              run every check
  python .charter/checks.py --only AC3   run one
  python .charter/checks.py --list       list ids
  python .charter/checks.py --anchor     print the three zero-change anchors
Exit 0 only when every requested check passes."""
import hashlib
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = chr(96)
BAR = chr(124)
BS = chr(92)
EXPECTED_HEAD = "d6eff20240adbcce327ca7cffe27053a6df6bd02"
GATE_ENUM = ("PENDING", "COMPLETE", "BLOCKED_TOOLING", "WAIVED", "NOT_STARTED")
READ_SET = ("project.md", "roadmap.md", "reuse-discovery.md", "current-task.md", "handoff.md", "lessons.md")
def contract_allowed():
    """The allowed paths, parsed from the leaf contract itself.

    The whitelist used to live here *and* in section 4 of the leaf contract: two copies
    of one rule, the exact defect REV-CHARTER-20 named (LS-004). The contract text is now
    the only source; this function only reads it."""
    t = read(".charter/current-task.md")
    parts = re.split(r"^### Allowed paths / artifacts\s*$", t, flags=re.M)
    if len(parts) < 2:
        return set(), ()
    sec = re.split(r"^### ", parts[1], flags=re.M)[0]
    exact, pref = set(), []
    for m in re.finditer(B + "([^" + B + "]+)" + B, sec):
        tok = m.group(1).strip()
        if tok.endswith("/**"):
            pref.append(tok[:-3].rstrip("/"))
        elif tok.endswith("/"):
            pref.append(tok[:-1])
        elif tok.endswith(".md") or tok.endswith(".json"):
            exact.add(tok)
    return exact, tuple(pref)


def read(p):
    return io.open(os.path.join(ROOT, p), encoding="utf-8").read()


def label_values(text, label):
    """Every value written on a line whose bullet label is `label` (one per projection point)."""
    pat = r"^\s*-\s*" + re.escape(label) + r"(?:[^:\n]*): (.+)$"
    return [m for m in re.findall(pat, text, re.M)]


def head_value(text, label):
    """First space-delimited token of the value, backticks and parenthetical tail removed."""
    vals = label_values(text, label)
    out = []
    for v in vals:
        v = v.split(chr(65288))[0].strip()
        v = v.split(" / ")[0].strip()
        v = v.split(chr(8212))[0].strip()
        out.append(v.strip().strip(B).strip())
    return out


def split_cells(line):
    """Escape-aware cell split: a bar preceded by a backslash is content, not a delimiter."""
    cells = []
    cur = []
    esc = False
    for ch in line:
        if esc:
            cur.append(ch)
            esc = False
        elif ch == BS:
            cur.append(ch)
            esc = True
        elif ch == BAR:
            cells.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    cells.append("".join(cur))
    return cells


def cell_count(line):
    return len(split_cells(line)) - 2


def run_bytes(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True)
    return p.returncode, p.stdout


def run(cmd):
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def ac_blocks():
    """Documented extraction rule: AC marker to the next AC marker or the next heading."""
    t = read(".charter/current-task.md")
    marks = [(m.start(), m.group(1)) for m in re.finditer(r"- \[ \] " + B + r"(AC[0-9]+)" + B, t)]
    out = []
    for i, (pos, aid) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(t)
        h = re.compile(r"(?m)^#{2,3} ").search(t, pos)
        if h and h.start() < end:
            end = h.start()
        out.append((aid, t[pos:end]))
    return out


# ---------------------------------------------------------------- checks

def check_ac1():
    missing = [f for f in READ_SET if not read(".charter/" + f).strip()]
    leaf = read(".charter/current-task.md")
    rd = read(".charter/roadmap.md")
    st = re.findall(r"(?m)^- Status: (.+)$", leaf)
    val = st[0].strip().strip(B) if st else None
    rows = [l for l in rd.splitlines() if l.strip().startswith(BAR)]
    hdr = [c.strip().strip(B) for c in split_cells(rows[0])]
    ci = hdr.index("Status") if "Status" in hdr else None
    hit = [c for c in [[x.strip().strip(B) for x in split_cells(r)] for r in rows[1:]]
           if len(c) > 2 and c[2] == "R1.1-S1-L1"]
    ok = (not missing) and len(st) == 1 and len(hit) == 1 and ci is not None and len(hit[0]) > ci and hit[0][ci] == val
    return ok, "missing=%s status=%r rows=%d" % (missing, val, len(hit))


def check_ac2():
    """No change outside the allowed paths: the worktree, and the commit range too."""
    exact, pref = contract_allowed()

    def allowed(p):
        return p in exact or any(p == a2 or p.startswith(a2 + "/") for a2 in pref)

    bl = read(".charter/evidence/baseline-2026-10-19.txt").splitlines()
    exp = [l.split(": ", 1)[1].strip().split()[0] for l in bl if l.startswith("# diff-sha256: ")]
    base_paths = set(l[3:].strip() for l in bl
                     if len(l) > 3 and l.strip() and not l.startswith("#") and l[3:].strip())
    def parse(lines):
        out = set()
        for l in lines:
            if len(l) > 3 and l[3:].strip():
                out.add((l[:2], l[3:].strip()))
        return out

    rc, out = run(["git", "status", "--porcelain"])
    cur = parse(out.splitlines())
    dirty_bad = [x for x in cur if not allowed(x[1])]

    rc2, dg = run_bytes(["git", "diff", "--", ".",
                         ":(exclude).charter", ":(exclude)docs/SELF-AUDIT.md",
                         ":(exclude)portable/templates/review.md",
                         ":(exclude)portable/references/contract-migrations.md",
                         ":(exclude)targets", ":(exclude)skills",
                         ":(exclude)plugins", ":(exclude).codex-plugin"])
    sha = hashlib.sha256(dg).hexdigest()
    # vacuous while the baseline bytes are no longer uncommitted; binding again if they
    # reappear as a diff, which then has to be exactly the baseline diff.
    dirty_ok = (not dg) or (bool(exp) and exp[0] == sha)

    rc3, names = run(["git", "diff", "--name-only", EXPECTED_HEAD + "..HEAD"])
    committed = [n.strip() for n in names.splitlines() if n.strip()]
    committed_bad = [n for n in committed if not allowed(n) and n not in base_paths]

    ok = (not dirty_bad) and dirty_ok and (not committed_bad) and bool(exact or pref)
    return ok, "whitelist=%dE/%dP dirty_bad=%s dirty=%d diff=%s committed=%d committed_bad=%s" % (
        len(exact), len(pref), dirty_bad[:4], len(cur), sha[:12], len(committed), committed_bad[:4])


def check_ac3():
    pj = read(".charter/project.md")
    rm = read(".charter/roadmap.md")
    rs = read(".charter/reuse-discovery.md")
    ct = read(".charter/current-task.md")
    gate = {"project.s1": head_value(pj, "Reuse discovery gate"),
            "project.s61": head_value(pj, "Gate result and reviewed on"),
            "roadmap": head_value(rm, "Reuse discovery gate"),
            "reuse": head_value(rs, "Gate status")}
    fresh = {"project.s61": head_value(pj, "Reuse discovery freshness"),
             "roadmap": head_value(rm, "Discovery freshness"),
             "reuse": head_value(rs, "Gate freshness for this leaf")}
    rid = {"project.s61": head_value(pj, "Reuse discovery ID"),
           "roadmap": head_value(rm, "Reuse discovery ID"),
           "reuse": head_value(rs, "Discovery ID")}
    leaf = {"material": head_value(ct, "Reuse assessment"),
            "coverage": label_values(ct, "Reuse coverage / result"),
            "route": label_values(ct, "Reuse final route / candidate IDs")}
    bad = []
    route = []

    def uniform(name, d, enum=None, prefix=None):
        vals = [v[0] for v in d.values() if len(v) == 1]
        for k, v in d.items():
            if len(v) != 1:
                bad.append((name, k, "matches=%d" % len(v)))
        if len(vals) != len(d) or len(set(vals)) != 1 or not vals[0]:
            bad.append((name, "values", sorted(set(vals))))
            return None
        if enum and vals[0] not in enum:
            bad.append((name, "enum", vals[0]))
        if prefix and not vals[0].startswith(prefix):
            bad.append((name, "shape", vals[0]))
        return vals[0]

    gv = uniform("gate", gate, enum=GATE_ENUM)
    uniform("freshness", fresh)
    uniform("RD", rid, prefix="RD-")
    if len(leaf["material"]) != 1 or len(leaf["coverage"]) != 1:
        bad.append(("leaf", "matches", (leaf["material"], leaf["coverage"])))
    else:
        mt = head_value(rs, "Material target test")
        if len(mt) != 1 or leaf["material"][0].strip().strip(B) != mt[0]:
            bad.append(("leaf.material", leaf["material"][0], mt))
        cov = [x.strip().strip(B) for x in leaf["coverage"][0].split(" / ")]
        log = [l for l in rs.splitlines() if l.startswith(BAR + " SR-")]
        hdr = [l for l in rs.splitlines() if l.startswith(BAR + " Record ")]
        if len(hdr) == 1 and log:
            hc = [c.strip().strip(B) for c in split_cells(hdr[0])]
            covs = sorted(set(split_cells(l)[hc.index("Coverage")].strip().strip(B) for l in log))
            ress = sorted(set(split_cells(l)[hc.index("Result")].strip().strip(B) for l in log))
            if len(cov) != 2 or covs != [cov[0].strip().strip(B)] or ress != [cov[1].strip().strip(B)]:
                bad.append(("leaf.coverage", cov, (covs, ress)))
        else:
            bad.append(("leaf.coverage", "no search log", len(log)))
        route = [v.split(" / ")[0].strip().strip(B) for v in leaf["route"]]
        cand = [l for l in rs.splitlines() if l.startswith(BAR + " C-")]
        chd = [l for l in rs.splitlines() if l.startswith(BAR + " ID ")]
        if len(route) == 1 and len(chd) == 1 and cand:
            hc = [c.strip().strip(B) for c in split_cells(chd[0])]
            di = [i for i, x in enumerate(hc) if x.startswith("Disposition")]
            ds = sorted(set(split_cells(l)[di[0]].strip().strip(B) for l in cand)) if di else []
            if ds != [route[0]]:
                bad.append(("leaf.route", route[0], ds))
        else:
            bad.append(("leaf.route", route, len(cand)))
    return (not bad), "gate=%s leaf=%s bad=%s" % (gv, route, bad[:4])


def check_ac4():
    rc, out = run([sys.executable, "scripts/validate_kit.py", "."])
    bad = [l for l in out.splitlines() if "FAIL" in l or "MISMATCH" in l.upper()]
    return (rc == 0 and not bad), "rc=%d bad=%s" % (rc, bad[:3])


def check_ac5():
    """History is not rewritten: HEAD must descend from the leaf's start revision."""
    rc, _ = run(["git", "merge-base", "--is-ancestor", EXPECTED_HEAD, "HEAD"])
    _, cnt = run(["git", "rev-list", "--count", EXPECTED_HEAD + "..HEAD"])
    _, h = run(["git", "rev-parse", "HEAD"])
    return (rc == 0), "head=%s start=%s commits_since_start=%s" % (
        h.strip()[:12], EXPECTED_HEAD[:12], cnt.strip())


def check_ac6():
    lines = read(".charter/project.md").splitlines()
    hdr = [l for l in lines if l.startswith(BAR + " ID " + BAR + " Question")]
    rows = [l for l in lines if l.startswith(BAR + " D-")]
    h = cell_count(hdr[0]) if len(hdr) == 1 else -1
    bad = [(split_cells(r)[1].strip(), cell_count(r)) for r in rows if cell_count(r) != h]
    return (len(hdr) == 1 and bool(rows) and not bad), "header=%d rows=%d bad=%s" % (h, len(rows), bad)


def check_ac7():
    bad = []
    seen = 0
    for f in sorted(os.listdir(os.path.join(ROOT, ".charter/records"))):
        m = re.search(r"REV-CHARTER-([0-9]+)", f)
        if not m or int(m.group(1)) < 19:
            continue
        seen += 1
        t = read(".charter/records/" + f)
        h = re.search(r"(?m)^## Checks performed[ ]*$", t)
        if not h:
            bad.append((f, "no section"))
            continue
        e = re.compile(r"(?m)^## ").search(t, h.end())
        seg = t[h.start():e.start() if e else len(t)]
        pat = re.compile(r"^- \[x\] " + B + "?CHK14" + B + "?")
        lines = [l for l in seg.splitlines() if pat.match(l)]
        if len(lines) != 1:
            bad.append((f, "CHK14 lines=%d" % len(lines)))
        elif not ("Exceptions claimed: none" in lines[0]
                  or all(k in lines[0] for k in ("item", "clause", "basis"))):
            bad.append((f, "exception not structured"))
    return (seen > 0 and not bad), "records=%d bad=%s" % (seen, bad)


def check_ac8():
    bad = []
    for aid, blk in ac_blocks():
        if blk.count("check: ") != 1:
            bad.append((aid, "check labels=%d" % blk.count("check: ")))
            continue
        after = blk.split("check: ", 1)[1]
        m = re.search(B + "([^" + B + "]+)" + B, after)
        if not m:
            bad.append((aid, "no payload"))
        elif BAR in m.group(1):
            bad.append((aid, "bare pipe in payload"))
    return (not bad), "blocks=%d bad=%s" % (len(ac_blocks()), bad)


def check_ac9():
    bad = []
    for aid, blk in ac_blocks():
        after = blk.split("check: ", 1)[1] if "check: " in blk else ""
        m = re.search(B + "([^" + B + "]+)" + B, after)
        want = "python .charter/checks.py --only " + aid
        if not m or m.group(1).strip() != want:
            bad.append((aid, m.group(1)[:60] if m else None))
    return (not bad), "bad=%s" % bad


CHECKS = [("AC1", check_ac1), ("AC2", check_ac2), ("AC3", check_ac3), ("AC4", check_ac4),
          ("AC5", check_ac5), ("AC6", check_ac6), ("AC7", check_ac7), ("AC8", check_ac8),
          ("AC9", check_ac9)]


def anchor():
    rc, a = run(["git", "ls-files", "-s"])
    rc, b = run(["git", "status", "--porcelain"])
    files = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(ROOT, ".charter")):
        dirnames[:] = sorted(d for d in dirnames if d != "__pycache__")
        for f in sorted(filenames):
            files.append(os.path.join(dirpath, f))
    h = hashlib.sha256()
    for f in sorted(files):
        rel = os.path.relpath(f, os.path.join(ROOT, ".charter")).replace(os.sep, "/")
        h.update(rel.encode("utf-8"))
        h.update(io.open(f, "rb").read())
    print("1 git-ls-files   ", hashlib.sha256(a.encode("utf-8")).hexdigest())
    print("2 git-status     ", hashlib.sha256(b.encode("utf-8")).hexdigest(), "lines", len(b.splitlines()))
    print("3 charter-content", h.hexdigest(), "files", len(files))


def main(argv):
    if "--anchor" in argv:
        anchor()
        return 0
    if "--list" in argv:
        print(" ".join(c[0] for c in CHECKS))
        return 0
    only = None
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]
    failed = 0
    for aid, fn in CHECKS:
        if only and aid != only:
            continue
        ok, detail = fn()
        print("%s %-4s %s" % ("ok  " if ok else "FAIL", aid, detail))
        if not ok:
            failed += 1
    print("RESULT", "PASS" if not failed else "FAIL(%d)" % failed)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

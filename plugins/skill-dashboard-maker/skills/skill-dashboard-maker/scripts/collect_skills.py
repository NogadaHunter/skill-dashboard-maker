#!/usr/bin/env python3
"""등록된 스킬 폴더를 훑어 스킬 목록(skills_raw.json)을 만든다.

사용:
  python3 collect_skills.py                      # 기본 위치를 자동으로 찾음
  python3 collect_skills.py --root /mnt/skills/user --out /tmp/skills_raw.json

각 스킬: name, description, path, files(SKILL.md 외 파일 수), file_list, size_kb, hash(SKILL.md SHA-1 앞 12자리), trigger_hints
표준 라이브러리만 사용한다.
"""
import argparse, hashlib, json, os, re, sys

DEFAULT_ROOTS = ["/mnt/skills/user", os.path.expanduser("~/.claude/skills")]
SKIP_NAMES = {"skill-dashboard-maker"}  # 대시보드를 만드는 이 스킬 자신은 목록에서 뺀다


def parse_frontmatter(text):
    """YAML 앞머리에서 name·description만 읽는다(외부 라이브러리 없이)."""
    m = re.match(r"^﻿?---\s*\n(.*?)\n---\s*(\n|$)", text, re.S)
    if not m:
        return {}
    lines = m.group(1).splitlines()
    out, i = {}, 0
    while i < len(lines):
        line = lines[i]
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not km:
            i += 1
            continue
        key, val = km.group(1), km.group(2).strip()
        if val in (">", "|", ">-", "|-", ">+", "|+", ""):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                block.append(lines[i].strip())
                i += 1
            joiner = "\n" if val.startswith("|") else " "
            out[key] = joiner.join(block).strip() if val != "" or block else ""
            continue
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        out[key] = val
        i += 1
    return out


def trigger_hints(desc, body):
    """'다음 상황에서 반드시…' 같은 트리거 목록을 힌트로 뽑는다(분석의 출발점일 뿐)."""
    hints = []
    for src in (desc, body[:6000]):
        for line in src.splitlines():
            t = line.strip()
            if t.startswith(("- ", "* ", "• ")) and len(t) < 160 and any(k in t for k in ("요청", "줘", "해줘", "만들", "언급", "작성")):
                hints.append(t[2:].strip())
    seen, uniq = set(), []
    for h in hints:
        if h not in seen:
            seen.add(h)
            uniq.append(h)
    return uniq[:12]


def find_root(explicit):
    if explicit:
        return explicit if os.path.isdir(explicit) else None
    for r in DEFAULT_ROOTS:
        if os.path.isdir(r) and any(os.path.isfile(os.path.join(r, d, "SKILL.md")) for d in os.listdir(r)):
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", help="스킬 폴더들이 들어 있는 위치 (기본: /mnt/skills/user → ~/.claude/skills)")
    ap.add_argument("--out", default="/tmp/skill-dashboard/skills_raw.json")
    a = ap.parse_args()

    root = find_root(a.root)
    if not root:
        print("NO_SKILLS_ROOT: 등록된 스킬 폴더를 찾지 못했어요. 찾아본 곳: " + ", ".join([a.root] if a.root else DEFAULT_ROOTS))
        sys.exit(2)

    skills = []
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d)
        md = os.path.join(p, "SKILL.md")
        if not os.path.isfile(md):
            continue
        text = open(md, encoding="utf-8", errors="replace").read()
        fm = parse_frontmatter(text)
        name = (fm.get("name") or d).strip()
        if name.lower() in SKIP_NAMES or d.lower() in SKIP_NAMES:
            continue
        body = re.sub(r"^﻿?---\s*\n.*?\n---\s*\n", "", text, count=1, flags=re.S)
        files = []
        for r, _, fs in os.walk(p):
            for f in fs:
                rel = os.path.relpath(os.path.join(r, f), p).replace(os.sep, "/")
                if rel != "SKILL.md":
                    files.append(rel)
        skills.append({
            "name": name,
            "folder": d,
            "description": fm.get("description", "").strip(),
            "path": md,
            "files": len(files),
            "file_list": sorted(files)[:30],
            "size_kb": round(len(text.encode("utf-8")) / 1024, 1),
            "hash": hashlib.sha1(text.encode("utf-8")).hexdigest()[:12],
            "trigger_hints": trigger_hints(fm.get("description", ""), body),
        })

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    json.dump({"root": root, "count": len(skills), "skills": skills}, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"FOUND {len(skills)} skills in {root} -> {a.out}")
    for s in skills:
        print(f"  - {s['name']}  ({s['size_kb']}KB, 부속 {s['files']}개)")


if __name__ == "__main__":
    main()

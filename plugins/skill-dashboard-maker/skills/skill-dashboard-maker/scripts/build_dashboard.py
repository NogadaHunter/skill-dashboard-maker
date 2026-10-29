#!/usr/bin/env python3
"""스킬 대시보드 HTML을 만들고, 갱신할 때 이전 대시보드와 비교한다. 표준 라이브러리만 사용.

1) 갱신 준비 (이전 대시보드 HTML이 있을 때)
   python3 build_dashboard.py plan --raw skills_raw.json --previous 이전.html --out-dir /tmp/skill-dashboard
   → reuse.json(그대로 쓸 항목), todo.txt(새로 분석할 스킬 이름) 생성, 추가·수정·삭제 목록 출력

2) 대시보드 생성
   python3 build_dashboard.py build --raw skills_raw.json --data reuse.json --data new_01.json [--data new_02.json ...]
        [--previous 이전.html] [--owner "사용자 이름"] [--title "제목 전체"] --out /mnt/user-data/outputs/skill-dashboard.html

   제목: --title이 있으면 그대로 → 없으면 --owner로 "<이름>의 스킬 대시보드"
        → 둘 다 없고 갱신이면 이전 대시보드의 이름·제목을 이어받음 → 그것도 없으면 "나의 스킬 대시보드"
"""
import argparse, datetime, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "dashboard-template.html")
MAKER_VERSION = "v1.1"
DEFAULT_TITLE = "나의 스킬 대시보드"
PLACEHOLDER = re.compile(r"^(\[.*\]|<.*>|O{2,}|ㅇ{2,}|○{2,}|내 ?이름|사용자 ?이름|이름 ?없이)$", re.I)
CATEGORY_ORDER = ["문서·보고서", "콘텐츠·마케팅", "교육·강의", "책·출판", "기획·분석", "영상·디자인", "데이터·자동화", "기타"]
REQUIRED = ["name", "ko_name", "category", "summary", "prompt"]
LISTS = ["triggers", "formats", "tips", "related"]


def load_json(p):
    return json.load(open(p, encoding="utf-8"))


def extract_previous(html_path):
    """이전 대시보드 HTML 안에 들어 있는 데이터를 꺼낸다."""
    html = open(html_path, encoding="utf-8").read()
    m = re.search(r'<script type="application/json" id="skill-data">(.*?)</script>', html, re.S)
    if not m:
        sys.exit("PREVIOUS_INVALID: 이 파일에서 대시보드 데이터를 찾지 못했어요. skill-dashboard-maker로 만든 HTML인지 확인해 주세요.")
    return json.loads(m.group(1).replace("<\\/", "</"))


def entries_from(files):
    items = []
    for f in files:
        d = load_json(f)
        items.extend(d["skills"] if isinstance(d, dict) and "skills" in d else d)
    return items


def key(name):
    return str(name or "").strip().lower()


def clean_owner(value):
    """사용자가 준 이름만 남긴다. 비었거나 자리표시자([내 이름], OOO 등)면 빈 문자열."""
    v = re.sub(r"\s+", " ", str(value or "")).strip().strip("'\"“”‘’")
    return "" if not v or PLACEHOLDER.match(v) else v[:30]


def source_label(root):
    """스킬 폴더 경로 대신 일반 문구만 남겨 PC 계정명 등이 대시보드에 찍히지 않게 한다."""
    r = str(root or "").replace("\\", "/")
    if r.startswith("/mnt/skills"):
        return "claude.ai 등록 스킬"
    if "/.claude/skills" in r:
        return "Claude Code 개인 스킬"
    return "등록 스킬 폴더"


def diff(raw, prev):
    """이름(대소문자 무시)으로 짝지어 추가·삭제·수정(SKILL.md 해시 변경)을 가린다."""
    prev_by = {key(s["name"]): s for s in prev.get("skills", [])}
    now_by = {key(s["name"]): s for s in raw["skills"]}
    added = sorted(now_by[k]["name"] for k in now_by if k not in prev_by)
    removed = sorted(prev_by[k]["name"] for k in prev_by if k not in now_by)
    updated = sorted(now_by[k]["name"] for k in now_by if k in prev_by and prev_by[k].get("hash") != now_by[k]["hash"])
    return added, removed, updated, prev_by


def cmd_plan(a):
    raw = load_json(a.raw)
    os.makedirs(a.out_dir, exist_ok=True)
    if a.previous:
        prev = extract_previous(a.previous)
        added, removed, updated, prev_by = diff(raw, prev)
        reuse = [prev_by[key(s["name"])] for s in raw["skills"] if key(s["name"]) in prev_by and s["name"] not in updated]
        todo = added + updated
        print(f"PREVIOUS {prev.get('generated_at', '?')}: 그대로 {len(reuse)} / 추가 {len(added)} / 수정 {len(updated)} / 삭제 {len(removed)}")
        print(f"OWNER {clean_owner(prev.get('owner')) or '(없음)'} | TITLE {prev.get('title', DEFAULT_TITLE)}")
        for label, lst in (("추가", added), ("수정", updated), ("삭제", removed)):
            if lst:
                print(f"  {label}: {', '.join(lst)}")
    else:
        reuse, todo = [], [s["name"] for s in raw["skills"]]
        print(f"NEW: 전체 {len(todo)}개를 분석해야 해요.")
    json.dump(reuse, open(os.path.join(a.out_dir, "reuse.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(a.out_dir, "todo.txt"), "w", encoding="utf-8").write("\n".join(todo))
    print(f"TODO {len(todo)} -> {os.path.join(a.out_dir, 'todo.txt')}")


def normalize(e, raw_by):
    e = dict(e)
    for k in LISTS:
        v = e.get(k, [])
        if isinstance(v, str):
            v = [x.strip() for x in re.split(r"\s*(?:/|,|\n)\s*", v) if x.strip()]
        e[k] = v
    sit = e.get("situations") or []
    e["situations"] = [x for x in sit if isinstance(x, dict) and x.get("prompt")]
    r = raw_by.get(key(e.get("name")))
    if r:  # 수집 단계의 사실 정보로 덮어쓴다
        e["name"] = r["name"]
        e["hash"] = r["hash"]
        e["files"] = r["files"]
    if e.get("category") not in CATEGORY_ORDER:
        e["category"] = "기타" if not e.get("category") else e["category"]
    return e


def cmd_build(a):
    raw = load_json(a.raw)
    raw_by = {key(s["name"]): s for s in raw["skills"]}
    merged = {}
    for e in entries_from(a.data):
        merged[key(e.get("name"))] = e  # 뒤에 준 파일이 우선
    problems, skills = [], []
    for s in raw["skills"]:
        e = merged.get(key(s["name"]))
        if not e:
            problems.append(f"MISSING {s['name']}: 분석 결과가 없어요")
            continue
        e = normalize(e, raw_by)
        miss = [k for k in REQUIRED if not str(e.get(k, "")).strip()]
        if miss:
            problems.append(f"INCOMPLETE {s['name']}: {', '.join(miss)} 비어 있음")
        skills.append(e)
    extra = sorted(merged[k].get("name", k) for k in set(merged) - set(raw_by))
    if extra:
        print("IGNORED(등록 목록에 없음): " + ", ".join(extra))
    if problems:
        print("\n".join(problems))
        if not a.force:
            sys.exit("BUILD_STOPPED: 위 스킬을 채운 뒤 다시 실행하세요(그대로 만들려면 --force).")

    present = {s["category"] for s in skills}
    cats = [c for c in CATEGORY_ORDER if c in present] + sorted(present - set(CATEGORY_ORDER))
    skills.sort(key=lambda s: (cats.index(s["category"]), s.get("ko_name") or s["name"]))

    prev = extract_previous(a.previous) if a.previous else None
    owner = clean_owner(a.owner) if a.owner is not None else clean_owner((prev or {}).get("owner"))
    title = (a.title or "").strip() or (prev.get("title") if prev and a.owner is None else "") or (f"{owner}의 스킬 대시보드" if owner else DEFAULT_TITLE)
    data = {
        "title": title[:60],
        "owner": owner,
        "generated_at": a.date or datetime.date.today().isoformat(),
        "source": source_label(raw.get("root", "")),
        "maker_version": MAKER_VERSION,
        "categories": cats,
        "skills": skills,
    }
    if prev:
        added, removed, updated, _ = diff(raw, prev)
        data["changes"] = {"previous_date": prev.get("generated_at", ""), "added": added, "removed": removed, "updated": updated}

    tpl = open(a.template, encoding="utf-8").read()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = tpl.replace("__SKILL_DATA__", payload).replace("__TITLE__", data["title"].replace("<", "&lt;"))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(html)
    print(f"BUILT {a.out}  '{data['title']}' · 스킬 {len(skills)}개 · 카테고리 {len(cats)}개 · {round(len(html.encode('utf-8')) / 1024)}KB")
    if "changes" in data:
        c = data["changes"]
        print(f"  변경: 추가 {len(c['added'])} / 수정 {len(c['updated'])} / 삭제 {len(c['removed'])}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--raw", required=True)
    p.add_argument("--previous")
    p.add_argument("--out-dir", default="/tmp/skill-dashboard")
    b = sub.add_parser("build")
    b.add_argument("--raw", required=True)
    b.add_argument("--data", action="append", required=True)
    b.add_argument("--previous")
    b.add_argument("--owner", help="대시보드 제목에 넣을 사용자 이름 (사용자에게서 받은 이름만)")
    b.add_argument("--title", help="사용자가 제목 전체를 지정했을 때만")
    b.add_argument("--date")
    b.add_argument("--template", default=TEMPLATE)
    b.add_argument("--out", default="/mnt/user-data/outputs/skill-dashboard.html")
    b.add_argument("--force", action="store_true")
    a = ap.parse_args()
    {"plan": cmd_plan, "build": cmd_build}[a.cmd](a)


if __name__ == "__main__":
    main()

# GitHub에 올리는 법 (저장소 주인용)

## 0. 올리기 전에

```bash
python tools/build_skill.py    # dist/skill-dashboard-maker.skill 다시 만들기
python tools/check_repo.py     # 구조 점검 (✔ 통과가 나와야 해요)
```

Claude Code CLI가 있으면 `claude plugin validate .` 도 돌려 보세요.

## 방법 1. GitHub 웹에서 올리기 (프로그램 설치 없이)

1. github.com 로그인 → 오른쪽 위 **+ → New repository**
2. Repository name: `skill-dashboard-maker`, **Public** 선택, README·LICENSE 추가는 체크하지 않기 → **Create repository**
3. 새 저장소 화면의 **uploading an existing file** 을 눌러, 이 폴더 안의 내용(폴더째)을 끌어다 놓기
   - `.claude-plugin` 처럼 점(.)으로 시작하는 폴더는 끌어다 놓을 때 빠지기 쉬워요. 올린 뒤 저장소에 `.claude-plugin/marketplace.json` 과 `plugins/skill-dashboard-maker/.claude-plugin/plugin.json` 이 보이는지 꼭 확인하세요. 없으면 Claude Code 설치가 안 돼요.
   - 빠졌다면 **Add file → Create new file** 에서 파일 이름 칸에 경로째(`.claude-plugin/marketplace.json`) 입력하고 내용을 붙여 넣어요.
4. 아래 Commit message에 `첫 공개 (v1.0.1)` → **Commit changes**

## 방법 2. git 명령으로 올리기

```bash
cd skill-dashboard-maker
git init
git add .
git commit -m "첫 공개 (v1.0.1)"
git branch -M main
git remote add origin https://github.com/NogadaHunter/skill-dashboard-maker.git
git push -u origin main
```

## 올린 뒤

- 저장소 오른쪽 **About** 의 톱니바퀴 → Description에 `등록된 Claude 스킬을 대시보드 HTML 한 장으로 정리하는 스킬`, Topics에 `claude-skills`, `claude-code-plugin`, `dashboard` 등을 넣으면 찾기 쉬워요.
- **Releases → Create a new release** → 태그 `v1.0.1` → `dist/skill-dashboard-maker.skill` 을 첨부하면, Claude.ai 사용자가 내려받기 편해요.
- 설치 시험: Claude Code에서 `/plugin marketplace add NogadaHunter/skill-dashboard-maker` → `/plugin install skill-dashboard-maker@peopleware-skill-dashboard`

## 고칠 때

1. `plugins/skill-dashboard-maker/skills/skill-dashboard-maker/` 안의 파일을 고친다
2. `plugin.json` 의 `version` 을 올린다 (예: 1.0.1 → 1.0.2). 안 올리면 이미 설치한 사람에게 업데이트가 안 가요
3. `CHANGELOG.md` 에 한 줄 적는다
4. `python tools/build_skill.py` → `python tools/check_repo.py` → 올리기

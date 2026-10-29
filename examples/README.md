# 예시 (가상 스킬 4개)

대시보드가 어떻게 생겼는지 보여 주려고 만든 **가상 스킬** 예시예요. 실제 스킬이 아니고, 이름도 모두 `example-`로 시작해요.

| 파일 | 단계 | 내용 |
|---|---|---|
| [`sample-skills/`](sample-skills/) | 1. 수집 | 가상 스킬 4개의 SKILL.md (문서·콘텐츠·교육·데이터 분야 하나씩) |
| [`sample-entries.json`](sample-entries.json) | 3. 스킬별 정리 | Claude가 SKILL.md를 읽고 `references/writing-guide.md` 형식대로 정리한 항목 |
| [`sample-skill-dashboard.html`](sample-skill-dashboard.html) | 4. 대시보드 | 완성된 대시보드. 내려받아 브라우저로 열어 보세요 (인터넷 없이 열려요) |

GitHub 화면에서는 HTML이 코드로 보여요. 파일을 열고 **Download raw file** 로 받은 뒤 더블클릭하면 대시보드로 열려요.

## 직접 돌려 보기

저장소 맨 위 폴더에서:

```bash
S=plugins/skill-dashboard-maker/skills/skill-dashboard-maker/scripts
python $S/collect_skills.py --root examples/sample-skills --out out/skills_raw.json
python $S/build_dashboard.py build --raw out/skills_raw.json --data examples/sample-entries.json \
  --title "예시 스킬 대시보드" --out out/skill-dashboard.html
```

갱신도 시험해 볼 수 있어요. 샘플 스킬 하나를 고치거나 지운 뒤 다시 수집하고, 이전 대시보드를 넘기면 바뀐 스킬만 골라내요.

```bash
python $S/build_dashboard.py plan --raw out/skills_raw.json \
  --previous examples/sample-skill-dashboard.html --out-dir out
```

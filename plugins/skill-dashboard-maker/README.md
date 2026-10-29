# skill-dashboard-maker

내 Claude에 등록된 스킬을 모두 읽어서 **스킬 대시보드 HTML 한 장**을 만들어 주는 플러그인이에요.
스킬마다 한국어 이름, 한 줄 요약, 입력·결과물, 바로 복사해 쓰는 기본·상황별 프롬프트를 정리하고, 검색·8개 카테고리 필터·라이트/다크 모드·휴대폰 화면을 지원해요.
이전 대시보드를 첨부하면 바뀐 스킬만 다시 정리하고 추가·수정·삭제 내역을 보여 줘요.

## 설치

```text
/plugin marketplace add NogadaHunter/skill-dashboard-maker
/plugin install skill-dashboard-maker@peopleware-skill-dashboard
```

## 쓰는 법

- 처음 만들기: `스킬 대시보드 만들어줘`
- 이름 지정: `[이름] 이름으로 스킬 대시보드 만들어줘`
- 갱신: (이전 `skill-dashboard.html` 첨부) `스킬 대시보드 갱신해줘`

Claude Code에서는 개인 스킬 폴더(`~/.claude/skills`)를 읽어요. 다른 위치는 "스킬 폴더는 [경로]야"라고 알려 주세요.

## 필요한 것

Python 3 (표준 라이브러리만 사용, 따로 설치할 것 없음)

자세한 설명과 예시: https://github.com/NogadaHunter/skill-dashboard-maker

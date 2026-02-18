# 📰 데일리 브리핑

> 매일 아침 8시 (KST), 글로벌 경제·기술·과학 뉴스를 자동으로 수집·요약·퍼블리싱하는 AI 뉴스 브리핑 서비스

🔗 **Live:** https://jinik0207.github.io/daily-briefing/

---

## 개요

OpenClaw + Claude AI 기반의 개인 뉴스 브리핑 자동화 시스템입니다.  
매일 아침 Brave Search API와 Time Magazine RSS를 통해 글로벌 뉴스를 수집하고,  
AI가 요약·분석한 브리핑을 GitHub Pages에 퍼블리싱한 뒤 Telegram으로 전송합니다.

---

## 주요 기능

### 📅 데일리 브리핑 (매일 08:00 KST)
- **경제** — 글로벌 주요 경제 뉴스 3~4건
- **기술/AI** — 최신 AI·기술 뉴스 2~3건
- **과학** — 주목할 과학·연구 뉴스 1~2건
- **Time 픽** — Time Magazine 당일 기사 중 AI 선별 2~3건
- **시장 동향** — 미국/아시아/유럽 주요 지수, USD/KRW 환율
- **💼 투자 조언 (AI 분석)** — 해외 투자 / 한국 투자 각각 분리 제공
  - 이전 브리핑 히스토리 기반 추세 반영
  - 투자 권유 아님 · 사실과 데이터 기반 분석
- **오늘의 포인트** — 핵심 한 줄 요약

### 📊 월간 요약 리포트 (매달 1일 09:00 KST)
- 전달 브리핑 전체를 요약한 월간 리포트 자동 생성
- 주요 이슈 요약, 시장 흐름, 핵심 테마·트렌드 정리
- 월간 투자 조언 (다음 달 전망 포함)

### 🌐 웹사이트
- **Daily / Monthly 탭** 분리
- **페이지네이션** — 7개/페이지, `?page=N` URL 파라미터 지원
- 각 브리핑은 개별 JSON 파일로 저장 → 초기 로드 빠름

---

## 요구사항

| 항목 | 내용 |
|------|------|
| [OpenClaw](https://openclaw.ai) | AI 에이전트 런타임 (cron, 도구 실행) |
| Python 3.8+ | 스크립트 실행 |
| [GitHub CLI (`gh`)](https://cli.github.com/) | repo 생성 및 Pages 설정 |
| [Brave Search API](https://api.search.brave.com/) | 뉴스 검색 (월 2,000 쿼리 무료) |
| Telegram Bot | 알림 수신 |

---

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/jinik0207/daily-briefing.git
cd daily-briefing
```

### 2. GitHub Pages 활성화

```bash
# GitHub CLI로 Pages 활성화 (main 브랜치 루트 기준)
gh repo edit --enable-pages
gh api repos/{owner}/{repo}/pages \
  -X POST \
  -f source[branch]=main \
  -f source[path]=/
```

또는 GitHub 웹에서: **Settings → Pages → Branch: main / root** 선택

### 3. OpenClaw에 Brave API 키 등록

```bash
# OpenClaw config에 Brave API 키 추가
openclaw config set brave_api_key YOUR_BRAVE_API_KEY
```

또는 OpenClaw 채팅에서:

```
Brave API 키 BSA... 를 openclaw config에 등록해줘
```

### 4. Telegram Bot 설정

1. [@BotFather](https://t.me/BotFather)에서 봇 생성 → 토큰 발급
2. OpenClaw config에 Telegram 채널 추가 (OpenClaw 문서 참고)

### 5. 스크립트 경로 설정

`scripts/publish_briefing.py`와 `scripts/generate_monthly.py`의 `REPO_DIR` 경로를  
본인의 로컬 repo 경로로 수정합니다.

```python
# scripts/publish_briefing.py, scripts/generate_monthly.py 상단
REPO_DIR = os.path.expanduser("~/.openclaw/workspace/daily-briefing")  # ← 본인 경로로 수정
```

### 6. Brave 쿼리 카운터 초기화

```bash
echo '{"count": 0, "limit": 970, "month": "YYYY-MM"}' \
  > ~/.openclaw/workspace/memory/brave-query-counter.json
```

### 7. OpenClaw Cron 등록

OpenClaw 채팅에서 아래와 같이 요청:

```
매일 아침 8시 KST에 데일리 브리핑 cron을 등록해줘.
매달 1일 9시 KST에 월간 리포트 cron도 등록해줘.
```

> Cron 프롬프트 상세 내용은 이 프로젝트의 기존 설정을 참고하거나, README 하단 **Cron 프롬프트** 섹션 참고.

---

## 실행

### 수동으로 브리핑 퍼블리싱

```bash
python3 scripts/publish_briefing.py \
  '## 🌍 경제\n- 뉴스 내용...' \
  '2026년 2월 18일 (수)' \
  '해외 투자 조언 텍스트' \
  '한국 투자 조언 텍스트'
```

### 수동으로 월간 리포트 생성

```bash
# 특정 월 브리핑 목록 확인
python3 scripts/generate_monthly.py list 2026-02

# 월간 리포트 생성 및 퍼블리싱
python3 scripts/generate_monthly.py \
  '2026-02' \
  '## 판 요약\n- 주요 이슈...' \
  '해외 월간 투자 조언' \
  '한국 월간 투자 조언'
```

### RSS 피드 파싱 (Time Magazine 예시)

```bash
# 오늘자 전체 기사 파싱
python3 scripts/parse_rss.py https://time.com/feed/ 100 "" today

# 특정 날짜 + 키워드 필터
python3 scripts/parse_rss.py https://time.com/feed/ 50 "AI,economy" 2026-02-18
```

### Brave 쿼리 카운터 확인

```bash
cat ~/.openclaw/workspace/memory/brave-query-counter.json
# {"count": 15, "limit": 970, "month": "2026-02"}
```

---

## 아키텍처

```
┌─────────────────────────────────────────┐
│           OpenClaw + Claude AI           │
│                                         │
│  [Cron 08:00 KST]  [Cron 매달 1일]     │
│       Daily              Monthly        │
└────────┬────────────────────┬───────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌────────────────────┐
│  뉴스 수집       │  │  월간 요약 생성     │
│                 │  │                    │
│ • Brave Search  │  │ • briefings/ 읽기  │
│   (경제/기술/    │  │ • AI 요약·분석     │
│    과학/시장)    │  │ • 투자 조언 생성   │
│ • Time RSS      │  └────────┬───────────┘
│ • NYT 검색      │           │
└────────┬────────┘           │
         │                    │
         ▼                    ▼
┌─────────────────────────────────────────┐
│           AI 분석 & 작성                 │
│                                         │
│ • 뉴스 요약 (각 섹션)                   │
│ • 이전 브리핑 히스토리 참조              │
│   (2개월 이내: briefings/*.json)        │
│   (2개월 초과: monthly/*.json)          │
│ • 투자 조언 Reasoning                   │
│   (해외 / 한국 분리)                    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│           퍼블리싱                       │
│                                         │
│  publish_briefing.py                    │
│  • Markdown → HTML 변환                 │
│  • briefings/YYYY-MM-DD.json 저장       │
│  • briefings/index.json 업데이트        │
│  • git commit & push → GitHub Pages    │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         Telegram 알림                   │
│  • 브리핑 요약 + 투자 조언 + 웹 URL     │
└─────────────────────────────────────────┘
```

---

## 파일 구조

```
daily-briefing/
├── index.html                  # 웹사이트 (Daily/Monthly 탭 + 페이지네이션)
├── scripts/
│   ├── publish_briefing.py     # 데일리 브리핑 퍼블리싱
│   ├── generate_monthly.py     # 월간 리포트 생성 + 오래된 브리핑 정리
│   └── parse_rss.py            # RSS 피드 파서
├── briefings/
│   ├── index.json              # 전체 날짜 목록 (최신순)
│   └── YYYY-MM-DD.json         # 개별 브리핑 파일
├── monthly/
│   ├── index.json              # 월간 리포트 목록
│   └── YYYY-MM.json            # 개별 월간 리포트
├── .gitignore
└── README.md
```

### 브리핑 JSON 스키마

```json
{
  "date": "2026년 2월 18일 (수)",
  "dateKey": "2026-02-18",
  "html": "<div class=\"section\">...",
  "generatedAt": "2026-02-18T01:00:00.000Z"
}
```

---

## 히스토리 참조 전략 (토큰 최적화)

| 기간 | 참조 소스 |
|------|-----------|
| 2개월 이내 | `briefings/*.json` (Daily 브리핑 개별 파일) |
| 2개월 초과 | `monthly/*.json` (월간 요약 리포트) |

월간 리포트 생성 시 2개월 초과 Daily 브리핑은 자동 삭제되어  
LLM 컨텍스트 사용량을 효율적으로 관리합니다.

---

## 기술 스택

| 구성요소 | 기술 |
|----------|------|
| AI | Claude (Amazon Bedrock) via OpenClaw |
| 뉴스 수집 | Brave Search API, RSS (Time Magazine) |
| 스크립트 | Python 3 |
| 퍼블리싱 | GitHub Pages |
| 알림 | Telegram Bot |
| 스케줄링 | OpenClaw Cron |

---

## Cron 스케줄

| 작업 | 스케줄 | 내용 |
|------|--------|------|
| 데일리 브리핑 | 매일 08:00 KST | 뉴스 수집 → 요약 → 퍼블리싱 → Telegram |
| 월간 리포트 | 매달 1일 09:00 KST | 전달 브리핑 요약 → 퍼블리싱 → Telegram |

---

## 보안 고려사항

- **API 키 / 토큰은 코드에 절대 포함하지 않습니다.**
- Brave API 키 → OpenClaw config에 저장
- Telegram Bot 토큰 → OpenClaw config에 저장
- GitHub 인증 → `gh` CLI credential 사용
- `.gitignore`로 `.env`, `secrets.json` 등 민감 파일 차단

---

*Built with [OpenClaw](https://openclaw.ai) · 2026-02-18*

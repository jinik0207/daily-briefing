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
├── briefings/
│   ├── index.json              # 전체 날짜 목록 (최신순)
│   └── YYYY-MM-DD.json         # 개별 브리핑 파일
└── monthly/
    ├── index.json              # 월간 리포트 목록
    └── YYYY-MM.json            # 개별 월간 리포트
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

## 스크립트

### `scripts/publish_briefing.py`
데일리 브리핑 퍼블리싱 스크립트

```bash
python3 publish_briefing.py '<markdown>' '<date>' '<advice_global>' '<advice_korea>'
```

- Markdown → HTML 변환
- `briefings/YYYY-MM-DD.json` 개별 파일 저장
- `briefings/index.json` 목록 업데이트
- git commit & push

### `scripts/generate_monthly.py`
월간 요약 리포트 생성 스크립트

```bash
# 월간 리포트 생성
python3 generate_monthly.py YYYY-MM '<markdown>' '<advice_global>' '<advice_korea>'

# 특정 월 브리핑 목록 확인
python3 generate_monthly.py list YYYY-MM
```

- `monthly/YYYY-MM.json` 생성
- `monthly/index.json` 업데이트
- **2개월 초과 Daily 브리핑 자동 정리** (generatedAt 기준)

### `scripts/parse_rss.py`
RSS 피드 파서 (Time Magazine 등)

```bash
python3 parse_rss.py <url> <max_items> "<keywords>" <today|YYYY-MM-DD>
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

*Built with [OpenClaw](https://openclaw.ai) · 2026-02-18*

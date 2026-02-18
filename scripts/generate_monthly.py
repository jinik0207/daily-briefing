#!/usr/bin/env python3
"""
월간 요약 리포트 생성 및 퍼블리싱
- briefings/index.json + briefings/YYYY-MM-DD.json에서 지정 월의 브리핑을 읽어 월간 요약 생성
- monthly/YYYY-MM.json에 저장
- 2개월 초과 Daily 브리핑 파일 자동 정리
사용법: python3 generate_monthly.py YYYY-MM '<월간요약 마크다운>' '<해외조언>' '<한국조언>'
"""

import sys
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.expanduser("~/.openclaw/workspace/daily-briefing")
BRIEFINGS_DIR = os.path.join(REPO_DIR, "briefings")
BRIEFINGS_INDEX = os.path.join(BRIEFINGS_DIR, "index.json")
MONTHLY_DIR = os.path.join(REPO_DIR, "monthly")
MONTHLY_INDEX = os.path.join(MONTHLY_DIR, "index.json")

def publish_monthly(year_month, markdown_text, advice_global=None, advice_korea=None):
    """월간 요약 리포트 생성 및 저장"""
    os.makedirs(MONTHLY_DIR, exist_ok=True)

    # publish_briefing의 md_to_html, render_investment_advice 재사용
    sys.path.insert(0, os.path.expanduser("~/.openclaw/workspace/scripts"))
    from publish_briefing import md_to_html, render_investment_advice

    html_content = md_to_html(markdown_text)
    if advice_global or advice_korea:
        html_content += render_investment_advice(advice_global, advice_korea)

    # 월간 리포트 저장
    monthly_path = os.path.join(MONTHLY_DIR, f"{year_month}.json")
    report = {
        "month": year_month,
        "html": html_content,
        "generatedAt": datetime.now(timezone.utc).isoformat()
    }
    with open(monthly_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ 월간 리포트 저장: {monthly_path}")

    # monthly/index.json 업데이트
    if os.path.exists(MONTHLY_INDEX):
        with open(MONTHLY_INDEX, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = []
    if year_month not in index:
        index.insert(0, year_month)
        with open(MONTHLY_INDEX, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    # 2개월 초과 브리핑 파일 정리
    pruned_files = prune_old_briefings()

    # Git push
    git_add = [f'monthly/{year_month}.json', 'monthly/index.json', 'briefings/index.json']
    git_add += [f'briefings/{f}' for f in pruned_files]
    cmds = [
        ['git', '-C', REPO_DIR, 'add'] + git_add,
        ['git', '-C', REPO_DIR, 'commit', '-m', f'monthly: {year_month} report + prune old briefings'],
        ['git', '-C', REPO_DIR, 'push', 'origin', 'main'],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return False
        if result.stdout.strip():
            print(result.stdout.strip())

    print(f"✅ 월간 리포트 퍼블리싱 완료: {year_month}")
    return True

def prune_old_briefings():
    """2개월 초과 Daily 브리핑 파일 정리. 삭제된 파일명 목록 반환."""
    if not os.path.exists(BRIEFINGS_INDEX):
        return []

    with open(BRIEFINGS_INDEX, 'r', encoding='utf-8') as f:
        index = json.load(f)

    cutoff = datetime.now(timezone.utc) - timedelta(days=60)
    kept = []
    removed = []

    for date_key in index:
        # date_key = "YYYY-MM-DD"
        try:
            dt = datetime.strptime(date_key, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            if dt < cutoff:
                # 파일 삭제
                path = os.path.join(BRIEFINGS_DIR, f"{date_key}.json")
                if os.path.exists(path):
                    os.remove(path)
                    removed.append(f"{date_key}.json")
                    print(f"🗑️  삭제: briefings/{date_key}.json")
                continue
        except ValueError:
            pass
        kept.append(date_key)

    if removed:
        with open(BRIEFINGS_INDEX, 'w', encoding='utf-8') as f:
            json.dump(kept, f, ensure_ascii=False, indent=2)
        print(f"🗑️  오래된 브리핑 {len(removed)}개 정리 완료")

    return removed

def get_briefings_for_month(year_month):
    """특정 월의 브리핑 목록 반환 (월간 요약 생성용)"""
    if not os.path.exists(BRIEFINGS_INDEX):
        return []

    with open(BRIEFINGS_INDEX, 'r', encoding='utf-8') as f:
        index = json.load(f)

    year, month = year_month.split('-')
    prefix = f"{year}-{month.zfill(2)}"
    result = []

    for date_key in index:
        if date_key.startswith(prefix):
            path = os.path.join(BRIEFINGS_DIR, f"{date_key}.json")
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    result.append(json.load(f))

    return result

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 generate_monthly.py YYYY-MM '<markdown>' [advice_global] [advice_korea]")
        print("\nTo list briefings for a month:")
        print("  python3 generate_monthly.py list YYYY-MM")
        sys.exit(1)

    if sys.argv[1] == 'list':
        year_month = sys.argv[2]
        items = get_briefings_for_month(year_month)
        print(f"{year_month} 브리핑 {len(items)}개:")
        for b in items:
            print(f"  - {b.get('date', 'unknown')} ({b.get('dateKey', '?')})")
        sys.exit(0)

    year_month = sys.argv[1]
    markdown = sys.argv[2]
    advice_g = sys.argv[3] if len(sys.argv) > 3 else None
    advice_k = sys.argv[4] if len(sys.argv) > 4 else None
    success = publish_monthly(year_month, markdown, advice_g, advice_k)
    sys.exit(0 if success else 1)

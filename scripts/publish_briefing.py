#!/usr/bin/env python3
"""
브리핑 퍼블리싱 스크립트 - 개별 파일 + 페이지네이션 방식
구조:
  briefings/index.json   - 전체 날짜 목록 (최신순)
  briefings/YYYY-MM-DD.json - 개별 브리핑
사용법: python3 publish_briefing.py '<markdown>' [date_str] [advice_global] [advice_korea]
"""

import sys
import json
import os
import re
import subprocess
from datetime import datetime, timezone, timedelta

REPO_DIR = os.path.expanduser("~/.openclaw/workspace/daily-briefing")
BRIEFINGS_DIR = os.path.join(REPO_DIR, "briefings")
BRIEFINGS_INDEX = os.path.join(BRIEFINGS_DIR, "index.json")

def md_to_html(md):
    lines = md.strip().split('\n')
    html = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('## '):
            text = line[3:]
            html.append(f'<div class="section"><div class="section-title">{text}</div>')
        elif line.startswith('---'):
            pass
        elif line.startswith('- '):
            content = line[2:]
            if '📎' in content:
                parts = content.split('📎')
                main_text = convert_inline(parts[0].strip())
                source_text = convert_inline('📎' + parts[1].strip())
                html.append(f'<div class="news-item"><p>{main_text}</p><p class="source">{source_text}</p></div>')
            else:
                html.append(f'<div class="news-item"><p>{convert_inline(content)}</p></div>')
        elif line.startswith('💡'):
            html.append(f'<div class="point">{convert_inline(line)}</div>')
        else:
            html.append(f'<p>{convert_inline(line)}</p>')
    result = '\n'.join(html)
    open_divs = result.count('<div class="section">') - result.count('</div>')
    result += '</div>' * max(0, open_divs)
    return result

def convert_inline(text):
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    return text

def render_investment_advice(advice_global, advice_korea):
    if not advice_global and not advice_korea:
        return ''
    global_html = f'''<div class="advice-section">
    <div class="advice-section-label">🌍 해외 투자</div>
    <p>{convert_inline(advice_global.strip())}</p>
  </div>''' if advice_global else ''
    korea_html = f'''<div class="advice-section">
    <div class="advice-section-label">🇰🇷 국내 투자 (한국)</div>
    <p>{convert_inline(advice_korea.strip())}</p>
  </div>''' if advice_korea else ''
    return f'''<div class="investment-advice">
  <div class="advice-title">💼 투자 조언 (AI 분석)</div>
  {global_html}
  {korea_html}
  <p class="disclaimer">⚠️ 본 내용은 AI가 생성한 참고용 정보이며, 투자 권유가 아닙니다. 투자 결정은 본인의 판단과 책임 하에 이루어져야 합니다.</p>
</div>'''

def publish(markdown_text, date_str=None, advice_global=None, advice_korea=None):
    kst = datetime.now(timezone(timedelta(hours=9)))

    # 날짜 문자열 (표시용)
    if not date_str:
        date_str = kst.strftime('%Y년 %m월 %d일 (%a)').replace(
            'Mon','월').replace('Tue','화').replace('Wed','수').replace(
            'Thu','목').replace('Fri','금').replace('Sat','토').replace('Sun','일')

    # 파일명용 날짜 키 (YYYY-MM-DD)
    date_key = kst.strftime('%Y-%m-%d')

    html_content = md_to_html(markdown_text)
    if advice_global or advice_korea:
        html_content += render_investment_advice(advice_global, advice_korea)

    # briefings/ 디렉토리 생성
    os.makedirs(BRIEFINGS_DIR, exist_ok=True)

    # 개별 브리핑 파일 저장
    briefing_path = os.path.join(BRIEFINGS_DIR, f"{date_key}.json")
    with open(briefing_path, 'w', encoding='utf-8') as f:
        json.dump({
            "date": date_str,
            "dateKey": date_key,
            "html": html_content,
            "generatedAt": datetime.now(timezone.utc).isoformat()
        }, f, ensure_ascii=False, indent=2)

    # index.json 업데이트 (최신순 날짜 키 목록)
    if os.path.exists(BRIEFINGS_INDEX):
        with open(BRIEFINGS_INDEX, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = []

    if date_key not in index:
        index.insert(0, date_key)
    else:
        # 이미 있으면 맨 앞으로
        index.remove(date_key)
        index.insert(0, date_key)

    # 최신순 정렬 유지
    index = sorted(set(index), reverse=True)

    with open(BRIEFINGS_INDEX, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    # Git push
    cmds = [
        ['git', '-C', REPO_DIR, 'add', f'briefings/{date_key}.json', 'briefings/index.json'],
        ['git', '-C', REPO_DIR, 'commit', '-m', f'briefing: {date_key}'],
        ['git', '-C', REPO_DIR, 'push', 'origin', 'main'],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return False
        if result.stdout.strip():
            print(result.stdout.strip())

    print(f"✅ 퍼블리싱 완료: {date_str} ({date_key})")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 publish_briefing.py '<markdown>' [date] [advice_global] [advice_korea]")
        sys.exit(1)
    md = sys.argv[1]
    date = sys.argv[2] if len(sys.argv) > 2 else None
    advice_g = sys.argv[3] if len(sys.argv) > 3 else None
    advice_k = sys.argv[4] if len(sys.argv) > 4 else None
    success = publish(md, date, advice_g, advice_k)
    sys.exit(0 if success else 1)

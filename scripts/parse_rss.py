#!/usr/bin/env python3
"""RSS 피드 파서 - 제목, 요약, 링크, 날짜, 카테고리만 추출"""

import sys
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import email.utils

def parse_rss(url, max_items=20, keywords=None):
    """RSS 피드를 파싱해서 제목/요약/링크/날짜/카테고리 추출"""
    
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; RSS Reader)'}
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=10) as response:
        content = response.read()
    
    root = ET.fromstring(content)
    channel = root.find('channel')
    
    items = []
    ns = {'content': 'http://purl.org/rss/1.0/modules/content/'}
    
    for item in channel.findall('item'):
        title = item.findtext('title', '').strip()
        link = item.findtext('link', '').strip()
        description = item.findtext('description', '').strip()
        pub_date = item.findtext('pubDate', '').strip()
        
        # 카테고리 목록
        categories = [c.text.strip() for c in item.findall('category') if c.text]
        
        # 날짜 파싱
        parsed_date = None
        if pub_date:
            try:
                parsed_date = email.utils.parsedate_to_datetime(pub_date)
                parsed_date = parsed_date.strftime('%Y-%m-%d %H:%M UTC')
            except:
                parsed_date = pub_date
        
        # HTML 태그 제거 (간단히)
        import re
        description = re.sub(r'<[^>]+>', '', description).strip()
        description = description[:300] + '...' if len(description) > 300 else description
        
        entry = {
            'title': title,
            'link': link,
            'description': description,
            'date': parsed_date,
            'categories': categories
        }
        
        # 키워드 필터링
        if keywords:
            text = (title + ' ' + description + ' ' + ' '.join(categories)).lower()
            if not any(kw.lower() in text for kw in keywords):
                continue
        
        items.append(entry)
        
        if len(items) >= max_items:
            break
    
    return items

if __name__ == '__main__':
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://time.com/feed/'
    max_items = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    keywords = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    # 날짜 필터: 'today' 또는 'YYYY-MM-DD' 형식
    date_filter = sys.argv[4] if len(sys.argv) > 4 else None

    items = parse_rss(url, max_items, keywords)

    if date_filter:
        if date_filter == 'today':
            from datetime import datetime, timezone
            today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        else:
            today = date_filter
        items = [i for i in items if i.get('date', '').startswith(today)]

    print(json.dumps(items, ensure_ascii=False, indent=2))

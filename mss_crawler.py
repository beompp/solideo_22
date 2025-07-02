import time
import requests
from bs4 import BeautifulSoup
import json
import sys
from datetime import datetime, timedelta
import re
import html

LIST_URL = "https://www.mss.go.kr/site/smba/ex/bbs/List.do?cbIdx=81"
VIEW_URL = "https://www.mss.go.kr/site/smba/ex/bbs/View.do?cbIdx=81&bcIdx={bcIdx}&parentSeq={parentSeq}"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def clean_text(text):
    # HTML 엔티티 치환 및 공백 정리
    text = html.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y.%m.%d")

def extract_between(text, start_kw, end_kw):
    start_idx = text.find(start_kw)
    if start_idx == -1:
        return ""
    start_idx += len(start_kw)
    end_idx = text.find(end_kw, start_idx)
    if end_idx == -1:
        return text[start_idx:].strip()
    return text[start_idx:end_idx].strip()

def get_detail_content(bcIdx, parentSeq, max_retry=3):
    url = VIEW_URL.format(bcIdx=bcIdx, parentSeq=parentSeq)
    for attempt in range(max_retry):
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            tr = soup.select_one('table tbody tr.m-block')
            if not tr:
                return ""
            textarea = tr.find('textarea')
            if not textarea:
                return ""
            text = textarea.get_text()
            return clean_text(text)
        except requests.exceptions.RequestException as e:
            print(f"상세페이지 요청 실패({attempt+1}/{max_retry}): {e}. 3초 후 재시도합니다.")
            time.sleep(3)
    return "[상세페이지 요청 실패]"

def crawl_notices(days):
    notices = []
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days-1)
    page = 1
    while True:
        params = {"cbIdx": 81, "pageIndex": page}
        try:
            res = requests.get(LIST_URL, params=params, headers=HEADERS, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"요청 실패: {e}. 3초 후 재시도합니다.")
            time.sleep(3)
            continue
        soup = BeautifulSoup(res.text, "html.parser")
        rows = soup.select("table tbody tr")
        if not rows:
            break
        stop = False
        for row in rows:
            tds = row.find_all("td")
            if len(tds) < 5:
                continue
            # title: 두 번째 td의 a 태그의 title 값
            a_tag = tds[1].find("a")
            if not a_tag or not a_tag.has_attr("onclick"):
                continue
            title = a_tag.get("title") or a_tag.get_text(strip=True)
            onclick = a_tag["onclick"]
            m = re.search(r"doBbsFView\('\d+','(\d+)'(?:,'\d+')*,'(\d+)'\)", onclick)
            if not m:
                continue
            bcIdx, parentSeq = m.group(1), m.group(2)
            # date: 다섯 번째 td의 텍스트
            date_str = tds[4].get_text(strip=True)
            reg_date = parse_date(date_str)
            if reg_date < start_date:
                stop = True
                break
            if reg_date > end_date:
                continue
            content = get_detail_content(bcIdx, parentSeq)
            notices.append({
                "title": title,
                "date": date_str,
                "content": content
            })
            time.sleep(0.5)  # 각 상세페이지 요청 사이에도 딜레이
        if stop:
            break
        page += 1
        time.sleep(1)  # 페이지 이동시 딜레이
    return notices

def embed_json_to_html(json_data, html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_text = f.read()
    # <script type="application/json" id="notices-data">...</script> 부분을 json_data로 교체
    new_html = re.sub(
        r'(<script type="application/json" id="notices-data">)(.*?)(</script>)',
        lambda m: m.group(1) + '\n' + json.dumps(json_data, ensure_ascii=False, indent=2) + '\n' + m.group(3),
        html_text,
        flags=re.DOTALL
    )
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

def main():
    if len(sys.argv) != 2:
        print("사용법: python crawl_notice.py N(며칠, 오늘 포함)\n예시: python crawl_notice.py 7")
        sys.exit(1)
    try:
        days = int(sys.argv[1])
        if days < 1:
            raise ValueError
    except ValueError:
        print("N은 1 이상의 정수여야 합니다.")
        sys.exit(1)
    notices = crawl_notices(days)
    with open("notices.json", "w", encoding="utf-8") as f:
        json.dump(notices, f, ensure_ascii=False, indent=2)
    print(f"{len(notices)}건 저장 완료 (notices.json)")
    embed_json_to_html(notices, 'mss_notice.html')
    print("mss_notice.html에 데이터가 embed 되었습니다.")

if __name__ == "__main__":
    main()
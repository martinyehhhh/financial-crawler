import requests
from bs4 import BeautifulSoup, Comment
from db.mysql import get_connection
import urllib3

# 忽略 SSL 警告（MOPS 網站的憑證格式有問題）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_financial_report(stock_id: str, year: int, season: int):
    url = f"https://mopsov.twse.com.tw/server-java/t164sb01?step=1&CO_ID={stock_id}&SYEAR={year}&SSEASON={season}&REPORT_ID=C"
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    print(f"正在抓取網址：{url}")
    res = requests.get(url, headers=headers, verify=False)
    print(f"HTTP 狀態碼：{res.status_code}")
    res.encoding = 'big5'  # 設定編碼為 big5
    print(f"抓取內容長度：{len(res.text)}")
    soup = BeautifulSoup(res.text, 'html.parser')
    print("解析 HTML 結束")
    result = []

    # 找到所有註解
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    print(f"找到 {len(comments)} 個註解")
    print(f"註解內容：{comments}")

    # 依序檢查每個註解，找出包含報表名稱的註解
    for comment in comments:
        if "資產負債表" in comment:
            statement_type = "balance_sheet"
            print("找到資產負債表")
            table = comment.find_next('table')  # 定位到資產負債表
        elif "綜合損益表" in comment or "損益表" in comment:
            statement_type = "income"
            table = comment.find_next('table')  # 定位到損益表
        elif "現金流量表" in comment:
            statement_type = "cash_flow"
            table = comment.find_next('table')  # 定位到現金流量表
        else:
            continue  # 非這三大表就跳過

        # 找到表格後的單位（rptidx 類別中）
        unit_span = table.find_next('div', class_='rptidx').find('span', class_='zh')
        unit = unit_span.text.strip() if unit_span else "未知"  # 預設為未知

        # 解析這個表格
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 3:  # 忽略無效的行
                continue

            account_code = cols[0].text.strip()  # 會計代碼
            item_name = cols[1].text.strip()  # 會計名稱

            # 取數值（第三欄的數字）
            value_text = cols[2].text.strip().replace(',', '').replace('--', '')
            try:
                value = int(value_text) if value_text else None
            except ValueError:
                value = None

            # 存入結果
            result.append({
                'stock_id': stock_id,
                'year': year,
                'season': f"Q{season}",
                'statement_type': statement_type,
                'account_code': account_code,
                'item_name': item_name,
                'value': value,
                'unit': unit  # 儲存單位
            })

    if not result:
        print(f"⚠️ 找不到財報資料：{stock_id} 年 {year} Q{season}")
    return result


def save_financial_report(report_data: list[dict]):
    if not report_data:
        print("⚠️ 沒有資料可儲存")
        return

    conn = get_connection()
    with conn.cursor() as cursor:
        for item in report_data:
            sql = """
                INSERT INTO financial_statements (
                    stock_id, year, season, statement_type,
                    account_code, item_name, value, unit
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    value=VALUES(value),
                    unit=VALUES(unit),
                    updated_at=CURRENT_TIMESTAMP
            """
            cursor.execute(sql, (
                item['stock_id'], item['year'], item['season'],
                item['statement_type'], item['account_code'],
                item['item_name'], item['value'], item['unit']
            ))
    conn.commit()
    conn.close()
    print(f"✅ 已成功寫入 {len(report_data)} 筆財報資料")


if __name__ == "__main__":
    stock_id = "1215"
    year = 2024
    season = 4

    print(f"🚀 抓取 股票代號：{stock_id} , {year} 年, Q{season} 財報中...")
    data = fetch_financial_report(stock_id, year, season)
    save_financial_report(data)
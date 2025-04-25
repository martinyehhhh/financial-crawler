import requests
from bs4 import BeautifulSoup
from db.mysql import get_connection
import urllib3

#  關掉 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def crawl_company_list():
    url = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # 加上 verify=False
    res = requests.get(url, headers=headers, verify=False)
    res.encoding = "big5"  # 網頁是 Big5 編碼
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.find("table", attrs={"class": "h4"})  # 主 table
    rows = table.find_all("tr")

    company_list = []
    for row in rows[1:]:  # 第一列是表頭
        cols = row.find_all("td")
        if len(cols) == 1 and "權證" in cols[0].text:
            print("✅ 偵測到權證欄位，中止爬取")
            break

        if len(cols) != 7:
            continue  # 不是公司資料列，略過

        name_col = cols[0].text.strip()
        if not name_col or '　' not in name_col:
            continue  # 沒有代號的列，也略過

        stock_id, name = name_col.split('　')
        isin_code = cols[1].text.strip()
        listing_date = cols[2].text.strip()
        market_type = cols[3].text.strip()
        industry = cols[4].text.strip()
        cfi_code = cols[5].text.strip()

        company_list.append({
            "stock_id": stock_id,
            "name": name,
            "isin_code": isin_code,
            "listing_date": listing_date,
            "market_type": market_type,
            "industry": industry,
            "cfi_code": cfi_code
        })

    return company_list

def save_companies(company_list):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 先抓出資料庫中所有還標記為在市的 stock_id
            cursor.execute("SELECT stock_id FROM companies WHERE is_listed = TRUE")
            existing_ids = set(row["stock_id"] for row in cursor.fetchall())

            # 新一輪爬到的 stock_id
            current_ids = set(item["stock_id"] for item in company_list)

            # ⬇找出這次沒出現在清單裡的現有公司（= 可能已下市）
            delisted_ids = existing_ids - current_ids

            # 將這些公司標記為下市
            if delisted_ids:
                format_strings = ','.join(['%s'] * len(delisted_ids))
                cursor.execute(
                    f"UPDATE companies SET is_listed = FALSE WHERE stock_id IN ({format_strings})",
                    tuple(delisted_ids)
                )
                print(f"偵測到下市公司 {len(delisted_ids)} 間，已更新 is_listed = FALSE")

            # 新增或更新爬蟲中的公司
            for item in company_list:
                sql = """
                    INSERT INTO companies (
                        stock_id, name, isin_code, listing_date,
                        market_type, industry, cfi_code, is_listed
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name),
                        isin_code=VALUES(isin_code),
                        listing_date=VALUES(listing_date),
                        market_type=VALUES(market_type),
                        industry=VALUES(industry),
                        cfi_code=VALUES(cfi_code),
                        is_listed=TRUE
                """
                cursor.execute(sql, (
                    item["stock_id"], item["name"], item["isin_code"],
                    item["listing_date"], item["market_type"],
                    item["industry"], item["cfi_code"]
                ))

        conn.commit()
        print(f"成功更新/新增 {len(company_list)} 筆公司資料")
    finally:
        conn.close()

if __name__ == "__main__":
    data = crawl_company_list()
    save_companies(data)
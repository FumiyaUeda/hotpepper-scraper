from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv, time, random, re

# — 設定項目 — 
TARGET_COUNT = 100    # 取得したい店舗件数
PAGE_LIMIT   = 10     # 最大ページ数（安全策）
MIN_DELAY    = 1.0    # リクエスト間スリープ：最小秒数
MAX_DELAY    = 3.0    # リクエスト間スリープ：最大秒数

# — ChromeDriver の設定 —
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
service = Service(executable_path="./chromedriver.exe")
driver  = webdriver.Chrome(service=service, options=options)
wait    = WebDriverWait(driver, 10)

csv_file  = "tokyo_restaurant_data_with_prices.csv"
shop_data = []

def fetch_detail_urls(page):
    url = f"https://www.hotpepper.jp/SA11/Y055/G001/?page={page}"
    driver.get(url)
    wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "h3.shopDetailStoreName > a")
    ))
    return [
        a.get_attribute("href")
        for a in driver.find_elements(By.CSS_SELECTOR, "h3.shopDetailStoreName > a")
        if a.get_attribute("href")
    ]

def fetch_store_info(driver, wait, url):
    """
    URL の詳細ページを開き、
    店名、ディナー予算、ランチ予算 をタプルで返す。
    """
    driver.get(url)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "p.headerShopName")))
    name = driver.find_element(By.CSS_SELECTOR, "p.headerShopName").text.strip()

    # area は元ループのロジックを流用
    area = driver.find_element(
        By.CSS_SELECTOR,
        "dd.shopInfoInnerItemArea.jscShopInfoInnerItem > p.shopInfoInnerItemTitle"
    ).text.strip()

    # 正規表現フィルタで予算を取得
    all_dd = driver.find_elements(By.CSS_SELECTOR, "dd")
    budgets = [dd.text.strip() for dd in all_dd if re.search(r'\d+～\d+円', dd.text)]
    dinner = lunch = ""
    if budgets:
        parts = budgets[0].split(maxsplit=1)
        dinner = parts[0]
        if len(parts) == 2:
            lunch = parts[1]

    return name, area, dinner, lunch

page = 1
seen = set()

print(f"▶ 目標件数: {TARGET_COUNT} 件 取得開始")

while len(shop_data) < TARGET_COUNT and page <= PAGE_LIMIT:
    print(f"\n▶ リストページ読み込み: {page} ページ目")
    detail_urls = fetch_detail_urls(page)

    for url in detail_urls:
        if url in seen:
            continue
        seen.add(url)

        # ここを関数呼び出しに置き換え
        name, area, dinner_price, lunch_price = fetch_store_info(driver, wait, url)
        shop_data.append([name, area, dinner_price, lunch_price, url])
        print(f"→ 取得 {len(shop_data):3d}: {name} / D:{dinner_price or '空欄'} / L:{lunch_price or '空欄'}")

        if len(shop_data) >= TARGET_COUNT:
            break

    page += 1
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

# CSV 出力
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "area", "dinner_price", "lunch_price", "url"])
    writer.writerows(shop_data)

print(f"\n✅ 完了: {len(shop_data)} 件 → {csv_file}")
driver.quit()

#!/usr/bin/env python3
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def fetch_page_source(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/115.0.0.0 Safari/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("Opening URL:", url)
    driver.get(url)
    
    time.sleep(5)  # 等頁面載入
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # 滾動到底部
    time.sleep(3)
    
    html = driver.page_source
    driver.quit()
    return html

def parse_dataset(html):
    soup = BeautifulSoup(html, "html.parser")
    records = []
    
    containers = soup.select("div.poi-list-cell-desktop-right-top-wrapper-main")
    if not containers:
        print("未能搵到餐廳容器，請檢查 HTML 結構!")
    
    for container in containers:
        name_elem = container.select_one("div.poi-name")
        if not name_elem:
            continue
        name = name_elem.get_text(strip=True)
        
        url_elem = container.select_one("a[href*='/zh/hongkong/restaurant/']")
        url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
        if url and not url.startswith('http'):
            url = "https://www.openrice.com" + url
        
        info_container = container.select_one("div.poi-list-cell-line-info")
        if info_container:
            spans = info_container.select("span.poi-list-cell-line-info-link")
            if len(spans) >= 4:
                cuisine = spans[1].get_text(strip=True)
                dish_type = spans[2].get_text(strip=True)
                price = spans[3].get_text(strip=True)
            else:
                cuisine = dish_type = price = ""
        else:
            cuisine = dish_type = price = ""
        
        rating_elem = container.select_one("span.score")
        rating = float(rating_elem.get_text(strip=True)) if rating_elem else 0.0
        
        review_elem = container.select_one("span.review-count")
        review_count = int(review_elem.get_text(strip=True).replace("則", "")) if review_elem else 0
        
        phone_elem = container.select_one("span.phone-number")
        phone = phone_elem.get_text(strip=True) if phone_elem else ""
        
        hours_elem = container.select_one("span.opening-hours")
        opening_hours = hours_elem.get_text(strip=True) if hours_elem else ""
        
        special_dish_elem = container.select_one("span.special-dish")
        special_dish = special_dish_elem.get_text(strip=True) if special_dish_elem else ""
        
        if name and cuisine and dish_type and price:
            records.append({
                "name": name,
                "cuisine": cuisine,
                "type": dish_type,
                "price": price,
                "phone": phone,
                "opening_hours": opening_hours,
                "rating": rating,
                "review_count": review_count,
                "special_dish": special_dish,
                "url": url
            })
        else:
            print("資料唔齊，跳過：", name)
            
    return records

def main():
    url = "https://www.openrice.com/zh/hongkong/restaurants/district/%E7%9F%B3%E5%A1%98%E5%92%80?sortBy=ORScoreDesc"
    html = fetch_page_source(url)
    
    dataset = parse_dataset(html)
    if dataset:
        with open("openrice_data.json", "w", encoding="utf8") as f:
            json.dump(dataset, f, ensure_ascii=False, indent=4)
        print("抓取完成，數據已存入 openrice_data.json")
    else:
        print("未有餐廳資料提取到。")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import json
import time
import csv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import logging
from typing import List, Dict

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_driver():
    """設置 Edge WebDriver"""
    try:
        edge_options = Options()
        edge_options.add_argument("--headless")  # 無頭模式
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Edge/115.0.0.0 Safari/537.36")
        
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=edge_options)
        return driver
    except Exception as e:
        logger.error(f"設置 WebDriver 失敗: {str(e)}")
        raise

def fetch_page_source(url: str) -> str:
    """從 URL 獲取頁面源碼"""
    driver = setup_driver()
    try:
        logger.info(f"正在打開 URL: {url}")
        driver.get(url)
        time.sleep(5)  # 等待頁面加載
        for _ in range(20):  # 多次滾動以確保加載所有內容
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
        
        html = driver.page_source
        return html
    except Exception as e:
        logger.error(f"獲取頁面源碼失敗: {str(e)}")
        return ""
    finally:
        driver.quit()

def parse_dataset(html: str, district_name: str) -> List[Dict]:
    """解析 HTML 並提取數據"""
    if not html:
        logger.warning("HTML 為空，跳過解析")
        return []
    
    soup = BeautifulSoup(html, "html.parser")
    records = []
    
    containers = soup.select("div.poi-list-cell-desktop-right-top-wrapper-main")
    if not containers:
        logger.warning("未能找到餐廳容器，請檢查 HTML 結構!")
        return []
    
    for container in containers:
        try:
            name_elem = container.select_one("div.poi-name")
            if not name_elem:
                continue
            name = name_elem.get_text(strip=True)
            
            url_elem = container.select_one("a[href*='/zh/hongkong/restaurant/']")
            url = url_elem['href'] if url_elem and 'href' in url_elem.attrs else ""
            if url and not url.startswith('http'):
                url = "https://www.openrice.com" + url
            
            info_container = container.select_one("div.poi-list-cell-line-info")
            cuisine = dish_type = price = ""
            if info_container:
                spans = info_container.select("span.poi-list-cell-line-info-link")
                if len(spans) >= 4:
                    cuisine = spans[1].get_text(strip=True)
                    dish_type = spans[2].get_text(strip=True)
                    price = spans[3].get_text(strip=True)
            
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
            
            address_elem = container.select_one("span.address")
            address = address_elem.get_text(strip=True) if address_elem else ""
            
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
                    "url": url,
                    "district": district_name,
                    "address": address
                })
            else:
                logger.warning(f"資料不齊全，跳過：{name}")
        except Exception as e:
            logger.error(f"解析數據時發生錯誤: {str(e)}")
            continue
            
    return records

def save_to_json(data: List[Dict], filename: str = "openrice_data.json"):
    """將數據保存到 JSON 文件"""
    try:
        with open(filename, "w", encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"數據已保存到 {filename}")
    except Exception as e:
        logger.error(f"保存 JSON 失敗: {str(e)}")

def json_to_csv(json_file: str, csv_file: str = "openrice_data.csv"):
    """將 JSON 轉換為 CSV"""
    try:
        with open(json_file, "r", encoding="utf8") as f:
            data = json.load(f)
        
        if not data:
            logger.warning("無數據可轉換!")
            return
        
        keys = data[0].keys()
        with open(csv_file, "w", newline="", encoding="utf8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"數據已轉換並保存到 {csv_file}")
    except Exception as e:
        logger.error(f"轉換 CSV 失敗: {str(e)}")

def main():
    districts = [
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E7%9F%B3%E5%A1%98%E5%92%80?sortBy=ORScoreDesc",  # Stone Nullah
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E4%B8%AD%E7%92%B0?sortBy=ORScoreDesc",           # Central
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E9%8A%85%E9%91%BC%E7%81%A3?sortBy=ORScoreDesc",   # Causeway Bay
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%97%BA%E8%A7%92?sortBy=ORScoreDesc",            # Mong Kok
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%B0%96%E6%B2%99%E5%92%81?sortBy=ORScoreDesc",   # Tsim Sha Tsui
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%9C%93%E7%81%B0?sortBy=ORScoreDesc",            # Wan Chai
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%8D%97%E5%8C%96?sortBy=ORScoreDesc",            # Southern
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%96%B0%E7%95%8C?sortBy=ORScoreDesc",            # New Territories
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%85%89%E8%8F%AF?sortBy=ORScoreDesc",            # Kwun Tong
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%B7%A6%E6%97%A7?sortBy=ORScoreDesc",            # Sai Kung
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%8F%A4%E9%9B%84?sortBy=ORScoreDesc",            # Kowloon City
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%92%8C%E5%B9%B3?sortBy=ORScoreDesc",            # Ho Man Tin
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%B7%87%E6%B0%B4%E6%9D%91?sortBy=ORScoreDesc",   # Sham Shui Po
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E9%95%B7%E6%B2%99%E7%81%A3?sortBy=ORScoreDesc",   # Cheung Sha Wan
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%B7%87%E9%84%89?sortBy=ORScoreDesc",            # Shatin
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%A2%85%E9%9B%B7%E9%84%89?sortBy=ORScoreDesc",   # Tai Po
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E5%A4%A7%E6%99%83?sortBy=ORScoreDesc",            # Tai Kok Tsui
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%9C%89%E5%85%B7%E8%A1%97?sortBy=ORScoreDesc",   # Yau Ma Tei
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%B7%87%E5%9C%93%E5%8C%96?sortBy=ORScoreDesc",   # Sham Wan
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E9%9D%92%E8%A3%94%E6%B9%96?sortBy=ORScoreDesc",   # Clear Water Bay
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%96%B0%E5%89%8D%E6%B9%96?sortBy=ORScoreDesc",   # Sai Wan Ho
        "https://www.openrice.com/zh/hongkong/restaurants/district/%E6%9C%89%E6%9C%89%E5%85%B7%E8%A1%97?sortBy=ORScoreDesc"  # Yau Yat Tsuen
    ]
    
    all_records = []
    total_districts = len(districts)
    
    for index, district_url in enumerate(districts, 1):
        logger.info(f"處理進度: {index}/{total_districts} - 地區: {district_url}")
        district_name = district_url.split("%E")[-1].split("?")[0]  # 提取地區名稱
        
        try:
            html = fetch_page_source(district_url)
            records = parse_dataset(html, district_name)
            all_records.extend(records)
            time.sleep(3)  # 增加延遲，避免被封鎖
        except Exception as e:
            logger.error(f"處理地區 {district_name} 失敗: {str(e)}")
            continue
    
    if all_records:
        save_to_json(all_records)
        json_to_csv("openrice_data.json")
    else:
        logger.error("無任何數據提取到。")

if __name__ == "__main__":
    main()
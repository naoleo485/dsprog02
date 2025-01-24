import requests
from bs4 import BeautifulSoup
import sqlite3
import time
from collections import Counter
import flet as ft

# データベース設定
DB_FILE = "kyujin.db"

# SQLite 初期化
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kyujin (
            JobCategory TEXT,
            Industry TEXT,
            KeyRequirements TEXT,
            OpenPosition TEXT,
            Features TEXT,
            EmploymentType TEXT,
            SalaryRange TEXT,
            Location TEXT,
            PRIMARY KEY (JobCategory, Industry, Location)
        )
    """)
    conn.commit()
    conn.close()

# 求人情報を保存する
def save_to_db(job_category, industry, key_requirements, open_position, features, employment_type, salary_range, location):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO kyujin (JobCategory, Industry, KeyRequirements, OpenPosition, Features, EmploymentType, SalaryRange, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (job_category, industry, key_requirements, open_position, features, employment_type, salary_range, location))
    conn.commit()
    conn.close()

def fetch_filtered_kyujin(keywords):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # SQLクエリで条件を適用
    query = "SELECT * FROM kyujin WHERE " + " AND ".join(f"Features LIKE '%{kw}%'" for kw in keywords)
    cursor.execute(query)

    results = cursor.fetchall()
    conn.close()
    return results

# マイナビ求人サイトをスクレイピング
def scrape_jobs(base_url):
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"HTTPリクエストエラー: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("div", class_="job-card")  # 適切なクラス名を確認

    for job in job_cards:
        try:
            job_category = job.find("span", class_="job-category").get_text(strip=True)
            industry = job.find("span", class_="industry").get_text(strip=True)
            key_requirements = job.find("ul", class_="key-requirements").get_text(strip=True)
            open_position = job.find("h2", class_="open-position").get_text(strip=True)
            features = ", ".join([f.get_text(strip=True) for f in job.find_all("span", class_="feature")])
            employment_type = job.find("span", class_="employment-type").get_text(strip=True)
            salary_range = job.find("span", class_="salary-range").get_text(strip=True)
            location = job.find("span", class_="location").get_text(strip=True)

            # データベースに保存
            save_to_db(job_category, industry, key_requirements, open_position, features, employment_type, salary_range, location)
        except AttributeError as e:
            print(f"データ解析エラー: {e}")
            continue

        # 1秒の遅延を追加
        time.sleep(1)

# データ分析
def analyze_data(data):
    # 勤務地分布
    locations = [row[7] for row in data]  # Location列を取得
    location_counts = Counter(locations)

    # 年収分布
    salary_ranges = [row[6] for row in data if row[6]]  # SalaryRange列を取得（空でない場合）
    salary_distribution = Counter(salary_ranges)

    return location_counts, salary_distribution

# Flet アプリのメイン関数
def main(page: ft.Page):
    page.title = "求人データ収集と分析"
    page.scroll = ft.ScrollMode.ALWAYS

    # 初期化
    initialize_db()
    
    # スクレイピング＆分析
    BASE_URL = "https://scouting.mynavi.jp/job-list/"
    scrape_jobs(BASE_URL)
    
    # フィルタリング条件
    keywords = ["フルリモート", "上場企業", "リーダー", "経営者", "部長", "課長", "年収"]

    # 条件に一致するデータを取得
    filtered_data = fetch_filtered_kyujin(keywords)

    # 分析
    location_counts, salary_distribution = analyze_data(filtered_data)

    # 勤務地分布を表示
    locations_column = ft.Column(
        [
            ft.Text("勤務地分布", size=18, weight="bold"),
        ] + [
            ft.Text(f"{location}: {count}件", size=14) for location, count in location_counts.items()
        ]
    )

    # 年収分布を表示
    salary_ranges_column = ft.Column(
        [
            ft.Text("年収分布", size=18, weight="bold"),
        ] + [
            ft.Text(f"{salary}: {count}件", size=14) for salary, count in salary_distribution.items()
        ]
    )

    # 分析結果をページに追加
    page.add(
        ft.Row(
            [
                ft.Container(content=locations_column, expand=1, padding=10),
                ft.Container(content=salary_ranges_column, expand=1, padding=10),
            ],
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
        )
    )

if __name__ == "__main__":
    ft.app(target=main) 

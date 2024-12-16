import json
import requests
import sqlite3
import datetime
import flet as ft

# データベース設定
DB_FILE = "weather.db"

# SQLite初期化
def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            area_code TEXT,
            date TEXT,
            weather TEXT,
            min_temp TEXT,
            max_temp TEXT,
            last_updated TIMESTAMP,
            PRIMARY KEY (area_code, date)
        )
    """)
    conn.commit()
    conn.close()

# DBに接続
con = sqlite3.connect("weather.db")

# SQL(RDBを操作するための言語）を実行するためのカーソルオブジェクトを取得
cur = con.cursor()

# 実行したいSQL
sql = 'CREATE TABLE weather(area_code, date, weather,min_temp,max_temp);'

# SQLを実行
cur.execute("""
    CREATE TABLE IF NOT EXISTS weather (
            area_code TEXT,
            date TEXT,
            weather TEXT,
            min_temp TEXT,
            max_temp TEXT,
            last_updated TIMESTAMP,
            PRIMARY KEY (area_code, date)
        )
    """)

# DBへの接続を閉じる
con.close()

# DBに接続
con = sqlite3.connect("weather.db")

# SQL（RDBを操作するための言語）を実行するためのカーソルオブジェクトを取得
cur = con.cursor()

# データを参照するSQL
# SELECT * FROM テーブル名;
# * の部分は，取得したい列の名前を，区切りで指定することもできる．
sql_select = "SELECT * FROM weather;"

# SQLを実行
cur.execute(sql_select)

for r in cur:
  print(r)

# DBへの接続を閉じる
con.close()

# データベースへのデータ保存関数
def save_weather_to_db(area_code, date, weather, min_temp, max_temp):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO weather (area_code, date, weather, min_temp, max_temp, last_updated)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (area_code, date, weather, min_temp, max_temp, datetime.datetime.now()))
    conn.commit()
    conn.close()

# データベースからデータ取得関数
def fetch_weather_from_db(area_code, date):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT weather, min_temp, max_temp, last_updated FROM weather
        WHERE area_code = ? AND date = ?
    """, (area_code, date))
    row = cursor.fetchone()
    conn.close()
    return row

# 地域データ読み込み関数
def load_areas(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# 天気データ取得関数（API利用）
def fetch_weather_from_api(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# 天気アイコン取得関数
def get_weather_icon(weather):
    if "晴" in weather:
        return ft.icons.WB_SUNNY
    elif "雨" in weather:
        return ft.icons.UMBRELLA
    elif "曇" in weather:
        return ft.icons.WB_CLOUDY
    elif "雪" in weather:
        return ft.icons.AC_UNIT
    else:
        return ft.icons.HELP

# 天気データ取得関数（DBとAPIを統合）
def get_weather_data(area_code):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    db_data = fetch_weather_from_db(area_code, today)
    if db_data:
        # DBデータが1時間以内に更新された場合は再利用
        last_updated = datetime.datetime.strptime(db_data[3], "%Y-%m-%d %H:%M:%S.%f")
        if (datetime.datetime.now() - last_updated).total_seconds() < 3600:
            return {
                "date": today,
                "weather": db_data[0],
                "min_temp": db_data[1],
                "max_temp": db_data[2],
            }

    # APIからデータを取得
    weather_data = fetch_weather_from_api(area_code)
    if "error" in weather_data:
        return {"error": weather_data["error"]}

    try:
        for i, date in enumerate(weather_data[0]["timeSeries"][0]["timeDefines"]):
            if date.startswith(today):
                weather = weather_data[0]["timeSeries"][0]["areas"][0]["weathers"][i]
                min_temps = weather_data[0]["timeSeries"][1]["areas"][0].get("tempsMin", ["-"])
                max_temps = weather_data[0]["timeSeries"][1]["areas"][0].get("tempsMax", ["-"])

                min_temp = min_temps[i] if i < len(min_temps) else "-"
                max_temp = max_temps[i] if i < len(max_temps) else "-"

                save_weather_to_db(area_code, date, weather, min_temp, max_temp)

                return {
                    "date": date,
                    "weather": weather,
                    "min_temp": min_temp,
                    "max_temp": max_temp,
                }
    except (IndexError, KeyError) as e:
        return {"error": f"データの解析中にエラーが発生しました: {e}"}

def create_weather_card(date, weather, min_temp, max_temp):
    weather_icon = ft.Icon(get_weather_icon(weather), size=40, color="orange")
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(date, size=16, weight="bold"),
                weather_icon,
                ft.Text(weather, size=14),
                ft.Row(
                    [
                        ft.Text(f"{min_temp}°C", size=12, color="blue"),
                        ft.Text(f"{max_temp}°C", size=12, color="red"),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=150,
        height=200,
        padding=10,
        border=ft.border.all(1, "lightgray"),
        border_radius=10,
        alignment=ft.alignment.center,
        bgcolor="#FFFFFF",
        shadow=ft.BoxShadow(blur_radius=5, color="lightgray"),
    )
    
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = ft.ScrollMode.ALWAYS
    page.bgcolor = "#E6E6E6"

    # 地域データ読み込み
    areas_file_path = "areas.json"  # ローカルに保存したファイル
    areas_data = load_areas(areas_file_path)

    weather_output = ft.GridView(
        expand=True,
        runs_count=2,  # 表示する列数
        spacing=20,
        run_spacing=10,
    )

    def load_weather(e):
        region_key = e.control.data
        if not region_key:
            weather_output.controls = [ft.Text("地域が選択されていません。")]
            page.update()
            return

        region_data = areas_data["centers"].get(region_key)
        children = region_data.get("children", [])

        # weather_cards の初期化
        weather_cards = []

        for child in children:
            if isinstance(child, str):
                area_code = child
            elif isinstance(child, dict) and "code" in child:
                area_code = child["code"]
            else:
                continue

            # DBまたはAPIから天気情報を取得
            weather_data = get_weather_data(area_code)
            if "error" in weather_data:
                weather_cards.append(ft.Text(f"エラー: {weather_data['error']}"))
                continue

            weather_cards.append(
                create_weather_card(
                    weather_data["date"],
                    weather_data["weather"],
                    weather_data["min_temp"],
                    weather_data["max_temp"],
                )
            )

        # weather_cards を weather_output に反映
        weather_output.controls = weather_cards
        page.update()

    # サイドバー作成
    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Text("地域を選択", size=18, weight="bold"),
            ],
            width=250,
            spacing=10,
        ),
        bgcolor="#F4F4F4",
        padding=10,
        border_radius=5,
    )

    for region_name, region_data in areas_data["centers"].items():
        region_display_name = region_data.get("name", region_name)  # 地名を取得、なければ番号を表示
        region_button = ft.Button(
            text=region_display_name,
            data=region_name,
            on_click=load_weather,  # 地域選択時の動作
        )
        sidebar.content.controls.append(region_button)  # Column にボタンを追加

    # レイアウト構成
    page.add(
        ft.Row(
            [
                sidebar,
                ft.Container(content=weather_output, expand=True, padding=20),
            ]
        )
    )

# メイン関数（省略箇所）
# サイドバー、カード作成、レイアウトなどは前述のコードを流用


if __name__ == "__main__":
    initialize_db()
    ft.app(target=main)
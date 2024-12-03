import json
import requests
import flet as ft

# 地域データ読み込み関数
def load_areas(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# 天気データ取得関数
def fetch_weather(area_code):
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

# カード作成関数
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

            weather_data = fetch_weather(area_code)
            if "error" in weather_data:
                weather_cards.append(ft.Text(f"エラー: {weather_data['error']}"))
                continue

            try:
                for i, date in enumerate(weather_data[0]["timeSeries"][0]["timeDefines"]):
                    weather = weather_data[0]["timeSeries"][0]["areas"][0]["weathers"][i]

                    min_temps = weather_data[0]["timeSeries"][1]["areas"][0].get("tempsMin", ["-"])
                    max_temps = weather_data[0]["timeSeries"][1]["areas"][0].get("tempsMax", ["-"])

                    min_temp = min_temps[i] if i < len(min_temps) else "-"
                    max_temp = max_temps[i] if i < len(max_temps) else "-"

                    weather_cards.append(create_weather_card(date, weather, min_temp, max_temp))
            except (IndexError, KeyError) as e:
                weather_cards.append(ft.Text(f"データの解析中にエラーが発生しました: {e}"))

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

if __name__ == "__main__":
    ft.app(target=main)










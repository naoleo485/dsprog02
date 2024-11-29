import json
import requests
import flet as ft

# areas.json をロード
def load_areas(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# 気象庁APIから天気データを取得
def fetch_weather(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# カードを作成するヘルパー関数
def create_weather_card(date, weather, min_temp, max_temp):
    return ft.Container(
        content=ft.Column(
            [
                ft.Text(date, size=16, weight="bold"),
                ft.Text(weather, size=14),
                ft.Row(
                    [
                        ft.Text(f"最低: {min_temp}°C", size=12),
                        ft.Text(f"最高: {max_temp}°C", size=12),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ],
            spacing=5,
        ),
        width=150,
        height=120,
        padding=10,
        border=ft.border.all(1, "lightgray"),
        border_radius=8,
    )

# メインアプリケーション
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = ft.ScrollMode.ALWAYS

    # 地域データの読み込み
    areas_file_path = "jma/areas.json"  # ファイルパスを調整
    areas_data = load_areas(areas_file_path)["centers"]

    # サイドバーに地域リストを表示
    region_dropdown = ft.Dropdown(
        label="地域を選択",
        options=[ft.dropdown.Option(key, value["name"]) for key, value in areas_data.items()],
        width=300,
    )
    weather_output = ft.Column(spacing=10)

    def show_weather(e):
        # 選択された地域
        selected_region_key = region_dropdown.value
        if not selected_region_key:
            weather_output.controls = [ft.Text("地域を選択してください。")]
            page.update()
            return

        selected_region = areas_data[selected_region_key]
        children_codes = selected_region.get("children", [])

        weather_cards = []
        for code in children_codes:
            weather_data = fetch_weather(code)
            if "error" in weather_data:
                weather_cards.append(ft.Text(f"エラー: {weather_data['error']}"))
                continue

            # 天気情報を処理
            for forecast in weather_data[0]["timeSeries"][0]["areas"]:
                if forecast["area"]["code"] == code:
                    for i, date in enumerate(weather_data[0]["timeSeries"][0]["timeDefines"]):
                        weather = forecast["weathers"][i]
                        min_temp = forecast.get("tempsMin", [None])[i] or "-"
                        max_temp = forecast.get("tempsMax", [None])[i] or "-"
                        weather_cards.append(create_weather_card(date, weather, min_temp, max_temp))

        # 出力を更新
        weather_output.controls = weather_cards if weather_cards else [ft.Text("天気情報がありません。")]
        page.update()

    # サイドバーの作成
    sidebar = ft.Container(
        content=ft.Column(
            [
                ft.Text("地域を選択", size=20, weight="bold"),
                region_dropdown,
                ft.ElevatedButton("天気を表示", on_click=show_weather),
            ],
            spacing=20,
        ),
        width=300,
        height=600,
        padding=10,
        bgcolor="#f4f4f4",
        border=ft.border.all(1, "lightgray"),
    )

    # ページレイアウト
    page.add(
        ft.Row(
            [
                sidebar,
                ft.Container(content=weather_output, padding=20, expand=True),
            ],
        )
    )

# 実行
if __name__ == "__main__":
    ft.app(target=main)







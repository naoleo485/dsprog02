import json
import requests
import flet as ft

# 地域データ読み込み
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
                ft.Text(date, size=14, weight="bold"),
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

# メインアプリケーション
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.scroll = ft.ScrollMode.ALWAYS

    # 地域データ読み込み
    areas_file_path = "jma/areas.json"  # ファイルパスを調整
    areas_data = load_areas(areas_file_path)["centers"]

    # 地域選択ドロップダウン
    region_dropdown = ft.Dropdown(
        label="地域を選択",
        options=[ft.dropdown.Option(key, value["name"]) for key, value in areas_data.items()],
        width=300,
    )
    weather_output = ft.Wrap(spacing=10, run_spacing=10)

    def show_weather(e):
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

            for forecast in weather_data[0]["timeSeries"][0]["areas"]:
                if forecast["area"]["code"] == code:
                    for i, date in enumerate(weather_data[0]["timeSeries"][0]["timeDefines"]):
                        weather = forecast["weathers"][i]
                        min_temp = forecast.get("tempsMin", [None])[i] or "-"
                        max_temp = forecast.get("tempsMax", [None])[i] or "-"
                        weather_cards.append(create_weather_card(date, weather, min_temp, max_temp))

        weather_output.controls = weather_cards if weather_cards else [ft.Text("天気情報がありません。")]
        page.update()

    # サイドバー作成
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
        padding=20,
        bgcolor="#f4f4f4",
        border=ft.border.all(1, "lightgray"),
        border_radius=10,
    )

    # レイアウト作成
    page.add(
        ft.Row(
            [
                sidebar,
                ft.Container(content=weather_output, padding=20, expand=True),
            ]
        )
    )

if __name__ == "__main__":
    ft.app(target=main)







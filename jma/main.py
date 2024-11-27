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
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

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

# メインアプリケーション
def main(page: ft.Page):
    page.title = "気象庁天気予報アプリ"
    page.scroll = ft.ScrollMode.ALWAYS

    # 地域データの読み込み
    areas_file_path = "jma/areas.json"  # ファイルパスを調整
    areas_data = load_areas(areas_file_path)["centers"]

    # UI 要素
    region_dropdown = ft.Dropdown(
        label="地域を選択してください",
        options=[ft.dropdown.Option(key, value["name"]) for key, value in areas_data.items()],
        width=300,
    )
    weather_output = ft.Text(value="天気情報がここに表示されます", size=16)

    def show_weather(e):
        # 選択された地域
        selected_region_key = region_dropdown.value
        if not selected_region_key:
           weather_output.value = "地域を選択してください。"
           page.update()
           return

        # 選択された地域の子地域を取得
        selected_region = areas_data[selected_region_key]
        children_codes = selected_region.get("children", [])

        # 天気データの取得と表示
        weather_details = []
        for code in children_codes:
            weather_data = fetch_weather(code)
            if "error" in weather_data:
                weather_details.append(f"エラー: {weather_data['error']}")
                continue

            # 天気情報を解析
            if weather_data:
                forecasts = weather_data[0]["timeSeries"][0]["areas"]
                for area in forecasts:
                    if area["area"]["code"] == code:
                        weather_details.append(
                            f"地域名: {area['area']['name']}\n")
                        weather_details.append(
                            f"天気: {area['weathers'][0]}\n")
                        # 気温の存在をチェック
                    if "temps" in area:
                        weather_details.append(f"気温: {area['temps']}°C")
                    else:
                        weather_details.append("気温データはありません。")    

        # 出力を更新
        weather_output.value = "\n".join(weather_details) if weather_details else "天気情報がありません。"
        page.update()

    # ボタン
    fetch_button = ft.ElevatedButton(text="天気を表示", on_click=show_weather)

    # レイアウトに追加
    page.add(
        ft.Column(
            [
                ft.Text("気象庁天気予報アプリ", size=24, weight="bold"),
                region_dropdown,
                fetch_button,
                weather_output,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

# 実行
if __name__ == "__main__":
    ft.app(target=main)







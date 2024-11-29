import json
import requests
import flet as ft

# 気象庁の地域リストを取得
AREA_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/"

def get_area_list():
    """地域リストを取得"""
    response = requests.get(AREA_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print("地域リストの取得に失敗しました。")
        return {}

def get_weather_forecast(area_code):
    """指定した地域コードの天気予報を取得"""
    url = f"{FORECAST_URL}{area_code}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("天気予報の取得に失敗しました。")
        return []

def display_forecast(forecast_data):
    """天気予報データを表示"""
    for forecast in forecast_data:
        for time_series in forecast.get("timeSeries", []):
            # 時間帯別の予報
            for i, area_data in enumerate(time_series.get("areas", [])):
                print(f"日時: {time_series['timeDefines'][i]}")
                print(f"天気: {area_data.get('weather', '情報なし')}")
                print(f"最低気温: {area_data.get('temps', ['--'])[0]}°C")
                print(f"最高気温: {area_data.get('temps', ['--'])[-1]}°C")
                print("-" * 20)

 # 地域選択をシミュレーション
    print("地域を選択してください：")
    print("例: 関東甲信地方 -> 010300")
    selected_area_code = input("地域コードを入力: ")

    # 天気予報取得
    forecast_data = get_weather_forecast(selected_area_code)
    if forecast_data:
        display_forecast(forecast_data)

# メイン処理
if __name__ == "__main__":
    area_list = get_area_list()






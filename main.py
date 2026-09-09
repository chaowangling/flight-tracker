import datetime
import smtplib
import os
from email.mime.text import MIMEText
import requests

# 從 GitHub Secrets 讀取金鑰
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

PRICE_LIMIT = 5000  # 價格門檻降至 5000 TWD

# 預設 30 天後出發，去 7 天
dep_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
arr_date = (datetime.date.today() + datetime.timedelta(days=37)).strftime("%Y-%m-%d")

# 觀察航線：台北桃園 -> 大阪關西
dep_code, dep_name = "TPE", "台北桃園"
arr_code, arr_name = "KIX", "大阪關西"

def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✉️ 成功發送低價通知信！")
    except Exception as e:
        print(f"❌ 寄信失敗: {e}")

def check_flights():
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_flights",
        "departure_id": dep_code,
        "arrival_id": arr_code,
        "outbound_date": dep_date,
        "return_date": arr_date,
        "currency": "TWD",
        "hl": "zh-TW",
        "gl": "tw",
        "api_key": SERPAPI_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        prices = []

        for cat in ["best_flights", "other_flights"]:
            if cat in data:
                for flight in data[cat]:
                    if "price" in flight:
                        prices.append(flight["price"])

        if prices:
            min_price = min(prices)
            print(f"[{dep_name} -> {arr_name}] 最低票價：NT$ {min_price:,}")
            if min_price <= PRICE_LIMIT:
                flight_url = f"https://www.google.com/travel/flights?q=Flights%20to%20{arr_code}%20from%20{dep_code}%20on%20{dep_date}%20through%20{arr_date}"
                subject = f"✈️ 超值大促銷！台北到大阪來回只要 NT$ {min_price:,}！"
                body = f"發現低於 NT$ {PRICE_LIMIT:,} 的神價機票！\n\n航線：{dep_name} -> {arr_name}\n日期：{dep_date} ~ {arr_date}\n目前最低價：NT$ {min_price:,}\n\n👉 立即前往 Google Flights 搶票：\n{flight_url}"
                send_email(subject, body)
        else:
            print(f"[{dep_name} -> {arr_name}] 未抓取到票價")

    except Exception as e:
        print(f"查詢失敗: {e}")

if __name__ == "__main__":
    check_flights()

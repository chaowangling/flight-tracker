import datetime
import smtplib
import os
from email.mime.text import MIMEText
import requests

# 從 GitHub Secrets 安全讀取金鑰
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
APP_PASSWORD = os.environ.get("APP_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")

PRICE_LIMIT = 20000

dep_date = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
arr_date = (datetime.date.today() + datetime.timedelta(days=37)).strftime("%Y-%m-%d")

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
        "departure_id": "TPE",
        "arrival_id": "NRT",
        "outbound_date": dep_date,
        "return_date": arr_date,
        "currency": "TWD",
        "hl": "zh-TW",
        "gl": "tw",
        "api_key": SERPAPI_KEY
    }

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
        print(f"最低票價：NT$ {min_price:,}")
        if min_price <= PRICE_LIMIT:
            subject = f"✈️ 促銷警報！Google Flights 低價機票：NT$ {min_price:,}"
            body = f"發現低價機票！\n日期：{dep_date} ~ {arr_date}\n目前最低價：NT$ {min_price:,}"
            send_email(subject, body)
    else:
        print("未抓取到票價")

if __name__ == "__main__":
    check_flights()

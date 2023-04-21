import requests
from datetime import datetime, timedelta 
from newsapi import NewsApiClient
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

TWILIO_SID = ""
TWILIO_AUTH_TOKEN = ""
TWILIO_VIRTUAL_NUMBER = ""
TWILIO_VERIFIED_NUMBER = ""

imogi = ""
yesterday = str() 
yesterdays_closing_price = float()
day_before_yesterday = str()
day_before_yesterdays_closing_price = float()

def get_dates():
    global yesterday, day_before_yesterday
    # checking if the day is sunday or saturday because market is closed on those days
    weekday = datetime.now().weekday()
    if weekday == 0:
        y = 3
        db = 4
    elif weekday == 1:
        y = 1 
        db = 4
    elif weekday == 6:
        y = 2 
        db = 3
    else:
        y = 1
        db = 2

    yesterday = (datetime.now() - timedelta(days = y)).strftime('%Y-%m-%d')
    day_before_yesterday = (datetime.now() - timedelta(days = db)).strftime('%Y-%m-%d')

def get_data():
    END_POINT = "https://www.alphavantage.co/query"
    STOCK_KEY = ""
    # enter key
     
    parameters = {
            # "function": "TIME_SERIES_INTRADAY",
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": "TSLA",
            # "interval": "60min",
            "apikey": STOCK_KEY
            }
     
    response = requests.get(url= END_POINT, params=parameters)
    response.raise_for_status()
    return response.json()

def compare_closing_price(data):
    global yesterdays_closing_price, day_before_yesterdays_closing_price, imogi

    yesterdays_closing_price = float(data['Time Series (Daily)'][yesterday]['4. close'])
    day_before_yesterdays_closing_price = float(data['Time Series (Daily)'][day_before_yesterday]['4. close'])

    difference = yesterdays_closing_price - day_before_yesterdays_closing_price
    if difference > 0:
        imogi = "🔺"
    else:
        imogi = "🔻"
    
    percentage = abs(difference)/yesterdays_closing_price * 100

    return percentage

def news_headline(difference):
    newsapi = NewsApiClient(api_key='')
    # enter api key

    top_headlines = newsapi.get_top_headlines(q='tesla',
                                              # sources='bbc-news,the-verge',
                                              category='business',
                                              language='en',
                                              country='us',
                                              page= 1)
     
    
    articles = top_headlines['articles'][:3]
    news = [f"TSLA: {imogi} {difference:.2f}%\nHeadline: {article['title']}.\nBreif: {article['description']}\nLink: {article['url']}" for article in articles]

    return news 

def send_sms(message_data):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        body=message_data,
        from_=TWILIO_VIRTUAL_NUMBER,
        to=TWILIO_VERIFIED_NUMBER,
    )
    print(message.sid)

get_dates()
data = get_data()
difference = compare_closing_price(data)
news = news_headline(difference)

for article in news:
    send_sms(article)

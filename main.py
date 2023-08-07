import datetime
import re
import googleapiclient.discovery
import google.auth
import tweepy
from local_settings import *
import unicodedata

# Google APIの準備をする
SCOPES = ['https://www.googleapis.com/auth/calendar']
calendar_id = 'cancaonova.chorus@gmail.com'
# Googleの認証情報をファイルから読み込む
gapi_creds = google.auth.load_credentials_from_file('./sa-key.json', SCOPES)[0]
# APIと対話するためのResourceオブジェクトを構築する
service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)

def extract_text_in_parentheses(text):
    pattern = r'[（(](.*?)[）)]'  # 括弧内の文字列をキャプチャするパターン
    if any(map(text.__contains__, ("(", "（"))):
        matches = re.findall(pattern, text)
        return matches[0]


# 指定された月のイベントを取得する関数
def get_events_in_month(year, month):
    # 指定された月の最初の日と最後の日を取得
    start_of_month = datetime.datetime(year, month, 1).isoformat() + 'Z'
    end_of_month = datetime.datetime(year, month+1, 1).isoformat() + 'Z'

    # イベントを取得する
    event_list = service.events().list(
        calendarId=calendar_id, timeMin=start_of_month, timeMax=end_of_month,
        singleEvents=True,
        orderBy='startTime').execute()

    # イベントの開始時刻、終了時刻、概要を取得する
    events = event_list.get('items', [])
    formatted_events = [(event['start'].get('dateTime', event['start'].get('date')),
                         event['end'].get('dateTime', event['end'].get('date')),
                         event['summary']) for event in events]

    # イベントを関西、関東、その他に分類して表示する
    kansai_events = []
    kanto_events = []
    other_events = []

    for event in formatted_events:
        if '関西' in event[2]:
            kansai_events.append(event)
        elif '関東' in event[2]:
            kanto_events.append(event)
        else:
            other_events.append(event)
    
    response = ''
    if kansai_events:
        response += '【関西】\n'
        for event in kansai_events:
            if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
                start_date = datetime.datetime.strptime(event[1], '%Y-%m-%d')
                response += f'{start_date.strftime("%#m/%#d")} @{extract_text_in_parentheses(event[2])} ({start_date.strftime("%H:%M")})\n'
            else:
                start_time = datetime.datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S+09:00')
                end_time = datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S+09:00')
                response += f'{start_time.strftime("%#m/%#d %#H:%M")}~{end_time.strftime("%#H:%M")} @{extract_text_in_parentheses(event[2])}\n'
        response += '\n'

    if kanto_events:
        response += '【関東】\n'
        for event in kanto_events:
            if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
                start_date = datetime.datetime.strptime(event[1], '%Y-%m-%d')
                response += f'{start_date.strftime("%#m/%#d")} @{extract_text_in_parentheses(event[2])} ({start_date.strftime("%H:%M")})\n'
            else:
                start_time = datetime.datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S+09:00')
                end_time = datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S+09:00')
                print(end_time)
                response += f'{start_time.strftime("%#m/%#d %#H:%M")}~{end_time.strftime("%#H:%M")} @{extract_text_in_parentheses(event[2])}\n'
        response += '\n'

    if other_events:
        response += '【全支部】\n'
        for event in other_events:
            if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
                start_date = datetime.datetime.strptime(event[1], '%Y-%m-%d')
                response += f'{start_date.strftime("%#m/%#d")} {event[2]}\n\n'
            else:
                start_time = datetime.datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S+09:00')
                end_time = datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S+09:00')
                a = re.split("[(（]", event[2])
                print(end_time)
                if extract_text_in_parentheses(event[2]) == None:
                    response += f'{start_time.strftime("%#m/%#d %H:%M")}~{end_time.strftime("%#H:%M")} {a[0]}\n'
                else:
                    response += f'{start_time.strftime("%#m/%#d %#H:%M")}~{end_time.strftime("%#H:%M")} {a[0]} @{extract_text_in_parentheses(event[2])}\n'
        response += '\n'

    response = response.rstrip('\n')
    return response


# 指定された月のイベントを取得して表示する
dt = datetime.datetime.now()
year = dt.year
month = dt.month + 1
list_rehearsal = get_events_in_month(year, month)

tweet_text = f"こんにちは!CancaoNovaです!\n{month}月の練習日程は\n\n{list_rehearsal}\n\nとなっております!"

print(tweet_text)

# Tweepyの認証
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def post_to_twitter(tweet):
    try:
        api.update_status(tweet)
        print("投稿が成功しました！")
    except tweepy.TweepError as e:
        print("投稿に失敗しました:", e.reason)

# # Twitterに投稿
# post_to_twitter(tweet_text)
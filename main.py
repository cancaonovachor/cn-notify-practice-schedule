import datetime
import re
import googleapiclient.discovery
import google.auth

# Google APIの準備をする
SCOPES = ['https://www.googleapis.com/auth/calendar']
calendar_id = 'cancaonova.chorus@gmail.com'
# Googleの認証情報をファイルから読み込む
gapi_creds = google.auth.load_credentials_from_file('./sa-key.json', SCOPES)[0]
# APIと対話するためのResourceオブジェクトを構築する
service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)

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

    # 出力テキストを生成する
    response = f'[{month}月の練習日程]\n'
    for event in formatted_events:
        if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
            start_date = '{0:%Y-%m-%d}'.format(datetime.datetime.strptime(event[1], '%Y-%m-%d'))
            response += f'{start_date} All Day\n{event[2]}\n\n'
        else:
            start_time = '{0:%Y-%m-%d %H:%M}'.format(datetime.datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S+09:00'))
            end_time = '{0:%H:%M}'.format(datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S+09:00'))
            response += f'{start_time} ~ {end_time}\n{event[2]}\n\n'
    response = response.rstrip('\n')
    print(response)

# 指定された月のイベントを取得して表示する
year = 2023
month = 6
get_events_in_month(year, month)

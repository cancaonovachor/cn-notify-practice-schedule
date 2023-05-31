import datetime, re
import googleapiclient.discovery
import google.auth


# ①Google APIの準備をする
SCOPES = ['https://www.googleapis.com/auth/calendar']
calendar_id = '自身のGoogleカレンダーIDを記述'
# Googleの認証情報をファイルから読み込む
gapi_creds = google.auth.load_credentials_from_file('./sa-key.json', SCOPES)[0]
# APIと対話するためのResourceオブジェクトを構築する
service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)


# ②Googleカレンダーからイベントを取得する
# 現在時刻を世界協定時刻（UTC）のISOフォーマットで取得する
now = datetime.datetime.utcnow().isoformat() + 'Z'
# 直近3件のイベントを取得する
event_list = service.events().list(
     calendarId=calendar_id, timeMin=now,
     maxResults=3, singleEvents=True,
     orderBy='startTime').execute()


# ③イベントの開始時刻、終了時刻、概要を取得する
events = event_list.get('items', [])
formatted_events = [(event['start'].get('dateTime', event['start'].get('date')), # start time or day
     event['end'].get('dateTime', event['end'].get('date')), # end time or day
     event['summary']) for event in events]


# ④出力テキストを生成する
response = '[直近イベント3件]\n'
# データの正規化をする
for event in formatted_events:
     if re.match(r'^\d{4}-\d{2}-\d{2}$', event[0]):
         start_date = '{0:%Y-%m-%d}'.format(datetime.datetime.strptime(event[1], '%Y-%m-%d'))
         response += '{0} All Day\n{1}\n\n'.format(start_date, event[2])
     # For all day events
     else:
         start_time = '{0:%Y-%m-%d %H:%M}'.format(datetime.datetime.strptime(event[0], '%Y-%m-%dT%H:%M:%S+09:00'))
         end_time = '{0:%H:%M}'.format(datetime.datetime.strptime(event[1], '%Y-%m-%dT%H:%M:%S+09:00'))
         response += '{0} ~ {1}\n{2}\n\n'.format(start_time, end_time, event[2])
response = response.rstrip('\n')
print(response)
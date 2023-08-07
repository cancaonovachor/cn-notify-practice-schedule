import datetime
import re
import googleapiclient.discovery
import google.auth
import tweepy
import unicodedata

# Twitter APIキーとトークン
API_KEY = "bWuWKrqOaTFL0Ne5OxCELZvg3"
API_SECRET = "6MHTfNxIRPmo50VMVU31nHm14592bgeJurp699y80IPmL2DUth"
ACCESS_TOKEN = "776029124288655360-4pGlehtBJmdfoU1Of5jOKRyX3SSM9oM"
ACCESS_TOKEN_SECRET = "bU5XYc75jvpFGmS6Gtc7cxsOowMRgxDtnrLLfqwtcopt0"

# Google APIの準備をする
SCOPES = ["https://www.googleapis.com/auth/calendar"]
calendar_id = "cancaonova.chorus@gmail.com"
gapi_creds = google.auth.load_credentials_from_file("./sa-key.json", SCOPES)[0]
service = googleapiclient.discovery.build("calendar", "v3", credentials=gapi_creds)


def remove_zero(s: str) -> str:
    return str(int(s))


def extract_text_in_parentheses(text):
    pattern = r"[（(](.*?)[）)]"
    if any(map(text.__contains__, ("(", "（"))):
        matches = re.findall(pattern, text)
        return matches[0]


def get_events_in_month(year, month):
    start_of_month = datetime.datetime(year, month, 1).isoformat() + "Z"
    end_of_month = datetime.datetime(year, month + 1, 1).isoformat() + "Z"
    event_list = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=start_of_month,
            timeMax=end_of_month,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = event_list.get("items", [])
    formatted_events = [
        (
            event["start"].get("dateTime", event["start"].get("date")),
            event["end"].get("dateTime", event["end"].get("date")),
            event["summary"],
        )
        for event in events
    ]

    kansai_events = []
    kanto_events = []
    other_events = []

    for event in formatted_events:
        if "関西" in event[2]:
            kansai_events.append(event)
        elif "関東" in event[2]:
            kanto_events.append(event)
        else:
            other_events.append(event)

    response = ""
    if kansai_events:
        response += "【関西】\n"
        for event in kansai_events:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", event[0]):
                start_date = datetime.datetime.strptime(event[1], "%Y-%m-%d")
                response += f'{remove_zero(start_date.strftime("%m"))}/{remove_zero(start_date.strftime("%d"))} @{extract_text_in_parentheses(event[2])} ({start_date.strftime("%H:%M")})\n'
            else:
                start_time = datetime.datetime.strptime(
                    event[0], "%Y-%m-%dT%H:%M:%S+09:00"
                )
                end_time = datetime.datetime.strptime(
                    event[1], "%Y-%m-%dT%H:%M:%S+09:00"
                )
                response += f'{remove_zero(start_time.strftime("%m"))}/{remove_zero(start_time.strftime("%d"))} {remove_zero(start_time.strftime("%H"))}:{start_time.strftime("%M")}~{remove_zero(end_time.strftime("%H"))}:{end_time.strftime("%M")} @{extract_text_in_parentheses(event[2])}\n'
        response += "\n"

    if kanto_events:
        response += "【関東】\n"
        for event in kanto_events:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", event[0]):
                start_date = datetime.datetime.strptime(event[1], "%Y-%m-%d")
                response += f'{remove_zero(start_date.strftime("%m"))}/{remove_zero(start_date.strftime("%d"))} @{extract_text_in_parentheses(event[2])} ({start_date.strftime("%H:%M")})\n'
            else:
                start_time = datetime.datetime.strptime(
                    event[0], "%Y-%m-%dT%H:%M:%S+09:00"
                )
                end_time = datetime.datetime.strptime(
                    event[1], "%Y-%m-%dT%H:%M:%S+09:00"
                )
                response += f'{remove_zero(start_time.strftime("%m"))}/{remove_zero(start_time.strftime("%d"))} {remove_zero(start_time.strftime("%H"))}:{start_time.strftime("%M")}~{remove_zero(end_time.strftime("%H"))}:{end_time.strftime("%M")} @{extract_text_in_parentheses(event[2])}\n'
        response += "\n"

    if other_events:
        response += "【全支部】\n"
        for event in other_events:
            if re.match(r"^\d{4}-\d{2}-\d{2}$", event[0]):
                start_date = datetime.datetime.strptime(event[1], "%Y-%m-%d")
                response += f'{remove_zero(start_date.strftime("%m"))}/{remove_zero(start_date.strftime("%d"))} {event[2]}\n\n'
            else:
                start_time = datetime.datetime.strptime(
                    event[0], "%Y-%m-%dT%H:%M:%S+09:00"
                )
                end_time = datetime.datetime.strptime(
                    event[1], "%Y-%m-%dT%H:%M:%S+09:00"
                )
                a = re.split("[(（]", event[2])
                if extract_text_in_parentheses(event[2]) == None:
                    response += f'{remove_zero(start_time.strftime("%m"))}/{remove_zero(start_time.strftime("%d"))} {start_time.strftime("%H:%M")}~{end_time.strftime("%H:%M")} {a[0]}\n'
                else:
                    response += f'{remove_zero(start_time.strftime("%m"))}/{remove_zero(start_time.strftime("%d"))} {start_time.strftime("%H:%M")}~{end_time.strftime("%H:%M")} {a[0]} (@{extract_text_in_parentheses(event[2])})\n'
        response += "\n"

    response = response.rstrip("\n")
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

# cn-notify-practice-schedule

練習予定を Nova カレンダーから取得して、自動で Twitter に投稿する

## デプロイ

```
# Docker ImageをArtifact Registryにpush
gcloud builds submit .
```

Cloud Run Jobs にデプロイをする

https://console.cloud.google.com/run/jobs?hl=ja&project=starlit-road-203901

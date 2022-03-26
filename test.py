from TikTokApi import TikTokApi

api = TikTokApi()

tag = api.hashtag(name="funny")

print(tag.info())

for video in tag.videos():
    print(video.id)
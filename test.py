
from TikTokApi import TikTokApi

verify_fp = ""
api = TikTokApi(custom_verify_fp=verify_fp)


tag = api.hashtag(name="funny")


print(tag.info())


for video in tag.videos():

    video_dict = video.as_dict

    print(video_dict['id'])
    print(video_dict['author'])

###########################################################


from TikTokApi import TikTokApi

verify_fp = ""
api = TikTokApi(custom_verify_fp=verify_fp)

for video in api.trending.videos():
    print(video.id)


#########################################################


from TikTokApi import TikTokApi

verify_fp = ""
api = TikTokApi(custom_verify_fp=verify_fp)

user = api.user(username="therock")

for video in user.videos():

    video_dict = video.as_dict

    print(video_dict['id'])
    print(video_dict['stats']['followerCount'])




from TikTokApi import TikTokApi

api = TikTokApi()

user_profile = api.user(username='haelstoot')
profile = user_profile.info_full()

print(profile)

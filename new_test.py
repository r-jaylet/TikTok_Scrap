from TikTokApi import TikTokApi

verify_fp = ""
api = TikTokApi(custom_verify_fp=verify_fp)

for user in api.search.users("therock"):
    print(user.username)
    print('\n' + 'zeubiiiiiiiiiiiiii')

for hashtag in api.search.hashtags("funny"):
    print(hashtag.name)

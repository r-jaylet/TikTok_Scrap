from TikTokApi import TikTokApi

api = TikTokApi.get_instance(custom_verifyFp='', use_test_endponts=True)
tiktok = api.get_user('the_rock')
print(tiktok)



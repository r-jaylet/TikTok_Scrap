from TikTokApi import TikTokApi
import pandas as pd

verifyFp = 'verify_kvfvyfh1_273CrYie_8lVQ_4p5v_BN6J_S3zGN19jmYWI'

api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endponts = True)

res = []
initial_list = ['music']
count = 10
for word in initial_list:
    l = api.search_for_hashtags(word, count=count, custom_verifyFp=verifyFp)
    for w in l:
        res.append(w)

res = initial_list + res
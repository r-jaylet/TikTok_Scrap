from TikTokApi import TikTokApi

def f():
    api = TikTokApi.get_instance(custom_verifyFp='', use_test_endponts=True)
    tiktok = api.by_hashtag('synth')
    print(tiktok)

f()


'''
hashtag_cand = ['music', 'musician', 'instrumentalist', 'impro',
               'solo', 'band', 'newmusic', 'musiciansoftiktok',
               'songwriter', 'rythm', 'cover',
               'jazztok', 'producer', 'guitarsolo'
               'jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
               'groove', 'classical', 'neosoul', 'indiemusic', 'lofi',
               'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro',
               'guitar', 'bass', 'piano', 'duetme', 'drums', 'synth', 'rhodes']



print(hashtag_cand[:100])
'''


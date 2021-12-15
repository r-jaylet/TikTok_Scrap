from TikTokApi import TikTokApi
import pandas as pd
from timeit import default_timer as timer

verifyFp = 'verify_kvfvyfh1_273CrYie_8lVQ_4p5v_BN6J_S3zGN19jmYWI'

api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endponts = True)

def tiktok(only_unverified = False, only_duo = False, bio_filter = False, hashtag_filter = False,
           n_iter = 1000, n_user = 100, n_vid = 6, max_followers = 10000000,
           seed = ['edmudbeats', 'terje_og_svein', 'sebisman92']):
    '''
    Creates a dataframe of musicians' profile on TikTok.
            Parameters:
                    only_unverified (bool): if 'True', only select unverified profiles
                    only_duo (bool): if 'True', only select 'duet/duo' interactions between musicians
                    bio_filter (bool): if 'True', only select musicians with selected key words in bio
                    hashtag_filter (bool): if 'True', only select musicians with selected key hashtags in videos' description
                    n_iter (int): maximum number of iterations on users
                    n_users (int): number of artists wanted in the database
                    n_vid (int): number of TikToks scrapped in each profile
                    max_followers (int): maximum number of followers
                    seed (list of str): list of users to initiate reccursive algorithm
            Returns:
                    user_df (dataframe): dataframe of users with its different characteristics
                        user_name (str): unique username of profile
                        user_id (int):  uniquer id of profile
                        sec_id (str): sec id of profile
                        signature (str): bio description of profile
                        nickname (str): nickname of user
                        verified (bool): is the user verified or not
                        follower_count (int):  number of followers
                        following_count (int): number of followings
                        likes_count (int): number of likes in total
                        video_count (int): number of videos on profile
                        collabs (list of str): list of username with which the user has collaborated
                        hashtags (list of str): list of unique hashtags used by user
    '''

    # initialize dataframe
    user_df = pd.DataFrame(columns = ['user_name', 'user_id', 'signature', 'nickname', 'verified',
                                    'follower_count', 'following_count', 'likes_count',
                                    'video_count', 'collabs', 'hashtags'])

    # initialize control variables
    i_iter = 0
    i_user = 0
    users = seed

    #create list of key words if key words filter activated
    '''
    search_for_hashtags doesn't seem to work anymore

    if bio_filter or hashtag_filter:

        key_hashtags = key_words
        for k in key_words:
            for c in api.search_for_hashtags(k, count=5, custom_verifyFp=verifyFp):
                key_hashtags.append(c['challenge']['title'])
        print('key words :', key_hashtags)
    '''
    key_hashtag = ['music', 'musician', 'instrumentalist', 'vocalist', 'singer', 'band',
                    'guitar', 'bass', 'piano', 'saxophone', 'guitartok',
                    'jazz', 'funk', 'rock', 'pop', 'rap', 'funk', 'rnb', 'neosoul', 'blues',
                    'sing', 'song', 'chanson', 'songwriter', 'singingchallenge',
                    'rythm', 'harmony', 'musicduet', 'soundtrack']

    for user in users:

        start = timer()
        i_iter+=1
        print('i_iter', i_iter, ':', user)

        try :
            profile = api.get_user(user, custom_verifyFp=verifyFp)  # get user profile

            if profile:  # check empty profil

                res = {}
                prof = profile['userInfo']['user']
                stat = profile['userInfo']['stats']
                tiktoks = profile['items']

                # check filters
                if bio_filter:
                    bio = prof['signature'].split()
                    if any([any(m in w for w in key_hashtag) for m in bio]):
                        res['signature'] = prof['signature']
                    else:
                        continue
                else:
                    res['signature'] = prof['signature']
                if only_unverified:
                    if prof['verified']:
                        continue
                    else:
                        res['verified'] = prof['verified']
                else:
                    res['verified'] = prof['verified']
                if stat['followerCount'] > max_followers:
                    continue
                else:
                    res['follower_count'] = stat['followerCount']

                # get profile info
                res['user_name'] = prof['uniqueId']
                res['user_id'] = prof['id']
                res['sec_id'] = prof['secUid']
                res['nickname'] = prof['nickname']

                # get stats
                res['following_count'] = stat['followingCount']
                res['likes_count'] = stat['heartCount']
                res['video_count'] = stat['videoCount']

                # get collab and hashtags
                if n_vid > 6:
                    profile = api.by_username(user, count = min(n_vid,res['video_count']), custom_verifyFp=verifyFp)

                collab, hashtag = [], []
                if tiktoks:
                    for tiktok in tiktoks:
                        if 'textExtra' in tiktok:  # get special text
                            if only_duo:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                if 'duo' in hashtag_cand or 'duet' in hashtag_cand or 'dúo' in hashtag_cand:
                                    collab_cand = list(filter(None, [text['userUniqueId'] for text in tiktok['textExtra']]))
                                    for collab_c in collab_cand:
                                        if collab_c not in collab :
                                            collab.append(collab_c)  # add collaborative artist
                                    for hashtag_c in hashtag_cand:
                                        if hashtag_c not in hashtag :
                                            hashtag.append(hashtag_c)   # add hashtag used
                                else:
                                    continue
                            else:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                collab_cand = list(filter(None, [text['userUniqueId'] for text in tiktok['textExtra']]))
                                for collab_c in collab_cand:
                                    if collab_c not in collab :
                                        collab.append(collab_c)  # add collaborative artist
                                for hashtag_c in hashtag_cand:
                                    if hashtag_c not in hashtag :
                                        hashtag.append(hashtag_c)   # add hashtag used

                # musician filter
                if hashtag_filter:
                    if any([any(m in w for w in key_hashtag) for m in hashtag]):  # a modifier
                        res['hashtags'] = hashtag
                        res['collabs'] = collab
                    else:
                        continue
                else:
                    res['hashtags'] = hashtag
                    res['collabs'] = collab

                user_df = user_df.append(res, ignore_index=True)  # update dataframe
                i_user+=1
                print('length data_base :', i_user)
                print('collab list of', user, 'is :', collab)

                end = timer()
                print('time :', end - start, '\n')

            for cand in collab:
                if cand not in users:
                    users.append(cand)

            # stop reccursion
            if i_iter >= n_iter:
                print('max threshold iteration')
                return user_df
            elif i_user >= n_user:
                print('max threshold users')
                return user_df

        except:
            print('error with user :', user)


    return user_df

df = tiktok(only_unverified = False, only_duo = False, bio_filter = False, hashtag_filter = True,
            n_iter = 1000, n_user = 200, n_vid = 18, max_followers = 100000000,
            seed = ['shannonlcallihan', 'johnmarknelson', 'sebisman92', 'dangelicony', 'judesmithmusic'])

df.to_csv('test_df1.csv', index=False)
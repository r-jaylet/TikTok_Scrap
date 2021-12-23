from TikTokApi import TikTokApi
import pandas as pd
from timeit import default_timer as timer
import csv
import sys

verifyFp = 'verify_kvfvyfh1_273CrYie_8lVQ_4p5v_BN6J_S3zGN19jmYWI'

api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endponts = True)

def tiktok(only_unverified = False, only_duo = False, hashtag_filter = True,
           n_user = 20, n_vid = 20, max_followers = 100000,
           seed = ['kissamile']):
    '''
    Creates a dataframe of musicians' profile on TikTok.
            Parameters:
                    only_unverified (bool): if 'True', only select unverified profiles
                    only_duo (bool): if 'True', only select 'duet/duo' interactions between musicians
                    bio_filter (bool): if 'True', only select musicians with selected key words in bio
                    hashtag_filter (bool): if 'True', only select musicians with selected key hashtags in videos' description
                    n_users (int): number of artists wanted in the database
                    n_vid (int): number of TikToks scrapped in each profile
                    max_followers (int): maximum number of followers
                    seed (list of str): list of users to initiate reccursive algorithm
            Returns:
                    user_df (dataframe): dataframe of users with its different characteristics
                        user_name (str): unique username of profile
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

    # initialize control variables
    i_iter = 0
    i_user = 0
    users = seed

    #create list of key words if key words filter activated

    key_hashtag = ['music', 'musician', 'instrumentalist', 'vocalist', 'singer', 'band', 'newmusic', 'musiciansoftiktok',
                   'guitar', 'bass', 'piano', 'guitartok', 'acoustic', 'drums',
                   'jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
                   'sing', 'song', 'singing', 'songwriter', 'acapella',
                   'rythm', 'harmony', 'cover']

    name_file = seed[0] + '_music.csv'
    fichier = open(name_file,'w', encoding="utf-8")
    obj = csv.writer(fichier)

    col_df = ['user_name', 'nickname', 'signature', 'verified', 'follower_count', 'following_count',
    'likes_count', 'video_count', 'collabs', 'hashtags']
    obj.writerow(col_df)

    for user in users:

        start = timer()
        i_iter+=1
        print('\n i_iter', i_iter, ':', user)

        try:
            profile = api.get_user(user, custom_verifyFp=verifyFp)  # get user profile

            if profile:  # check empty profil

                res = {'user_name' : '', 'nickname' :'', 'signature' : '', 'verified' :'',
                       'follower_count' : 0, 'following_count' :'', 'likes_count': 0, 'video_count' : 0,
                       'collabs' :'', 'hashtags' :''}

                prof = profile['userInfo']['user']
                stat = profile['userInfo']['stats']
                tiktoks = profile['items']

                # check filters
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
                res['signature'] = prof['signature']
                res['user_name'] = prof['uniqueId']
                res['nickname'] = prof['nickname']

                # get stats
                res['following_count'] = stat['followingCount']
                res['likes_count'] = stat['heartCount']
                res['video_count'] = stat['videoCount']

                # get collab and hashtags
                if n_vid > 6:
                    profile = api.by_username(user, count = n_vid, custom_verifyFp=verifyFp)
                    tiktoks = profile

                collab, hashtag = [], []
                if tiktoks:
                    for tiktok in tiktoks:
                        if 'textExtra' in tiktok:  # get special text
                            if only_duo:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                if ('duo' in hashtag_cand) or ('duet' in hashtag_cand) or ('duetwithme' in hashtag_cand) or ('duetthis' in hashtag_cand) or ('duets' in hashtag_cand):
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
                    if any([any(m in w for w in key_hashtag) for m in hashtag]):
                        res['hashtags'] = hashtag
                        res['collabs'] = collab
                    else:
                        continue
                else:
                    res['hashtags'] = hashtag
                    res['collabs'] = collab

                obj.writerow(tuple(res.values()))

                i_user+=1
                print('taille base de données :', i_user)
                print('liste de collaborateurs de', user, ':', collab)

                end = timer()
                print('temps éxécution :', round(end - start,3))

            for cand in collab:
                if cand not in users:
                    users.append(cand)

            if i_user >= n_user:
                print("Nombre d'utilisateurs voulu atteint")
                fichier.close()
                return

        except:
            print("\n Erreur avec l'utilisateur :", user)

    fichier.close()
    print("Plus d'utilisateurs sur lesquels itérer")
    return

if __name__ == '__main__':

    depart = int(input("Nombre d'utilisateurs avec lequel initialiser l'algortihme :"))

    print('Nom(s) de(s) utilisateurs(s) voulu(s) pour initialiser :')
    ini_list = []
    for i in range(depart):
        us = input()
        ini_list.append(us)

    arret = int(input("Nombre d'utilisateurs avec lequel terminer l'algortihme :"))

    tiktok(n_user = arret, seed = ini_list)
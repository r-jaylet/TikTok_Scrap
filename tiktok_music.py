from TikTokApi import TikTokApi
from timeit import default_timer as timer
import csv
from datetime import datetime
import time
import sys
import ast
import pandas as pd
from pyautogui import typewrite

verifyFp = 'verify_507ceffa7f90b24ef070f8e8558da484'

api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endponts=True)

# list of key words for filter
key_hashtag = ['music', 'musician', 'instrumentalist', 'impro',
               'solo', 'band', 'newmusic', 'musiciansoftiktok',
               'songwriter', 'rythm', 'cover',
               'jazztok', 'producer', 'guitarsolo'
               'jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
               'groove', 'classical', 'neosoul', 'indiemusic', 'lofi',
               'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro',
               'guitar', 'bass', 'piano', 'drums', 'synth', 'rhodes']

def tiktok(only_unverified=False,
           only_duo=False,
           hashtag_filter=True,
           list_hashtags=key_hashtag,
           n_user=20,
           n_vid=30,
           max_followers=100000,
           seed=None):
    """
    Creates a dataframe of musicians' profile on TikTok.
            Parameters:
                only_unverified (bool): if 'True', only select unverified profiles
                only_duo (bool): if 'True', only select duet connections
                hashtag_filter (bool): if 'True', only select musicians with selected key hashtags in videos' description
                n_user (int): number of artists wanted in the database
                n_vid (int): number of TikToks scrapped in each profile
                max_followers (int): maximum number of followers
                list_hashtags (list of str) : list of hashtags to filter musicians
                seed (list of str): list of users to initiate reccursive algorithm
            Returns:
                user_df (dataframe): dataframe of users with its different characteristics
                    user_name (str): unique username of profile
                    signature (str): bio description of profile
                    nickname (str): nickname of user
                    verified (bool): is the user verified or not
                    follower_count (int):  number of followers
                    following_count (int): number of followings
                    last_active (datetime): date of last posted video
                    likes_count (int): number of likes in total
                    video_count (int): number of videos on profile
                    mentions (list of str): list of username with which the user has mentioned
                    duos (list of str): list of username with which the user has dueted with
                    collabs (list of str): list of username with which all the user has collaborated
                    music_collabs (list of str): list of username of musicians with whom the user has collaborated
                    music_collabs_url (dic): dictionnary with urls of music_collabs' tiktoks
                    hashtags (list of str): list of unique hashtags used by user
                    styles (list of str): list of styles cited by user
                    instruments (list of str): list of instruments cited by user
    """
    # initialize control variables
    iter = 0
    i_user = 0
    pause = 0
    users = seed

    # list of key words for duos
    duo_list = ['duo', 'duet', 'duetme', 'duetwithme', 'duetthis', 'duets', 'duos']

    # list of key words for style and instruments
    style = ['jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
                'groove', 'classical', 'neosoul', 'indiemusic', 'lofi',
                'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro']
    instrument = ['guitar', 'bass', 'piano', 'drums', 'synth', 'rhodes',
                    'tuba', 'chords', 'saxophone', 'violin', 'flute', 'cello']

    # initialize csv doc
    name_file =  users[0] + '_' + str(n_user) + '_music.csv'
    file = open(name_file, 'w', encoding="utf-8")
    obj = csv.writer(file)

    col_df = ['user_name', 'nickname', 'signature', 'verified',
              'follower_count', 'following_count', 'likes_count', 'video_count',
              'last_active', 'mentions', 'duos', 'collabs', 'collabs_url',
              'hashtags', 'instruments', 'styles']
    obj.writerow(col_df)

    start_check = timer()
    for user in users:

        iter += 1
        print('\n')
        print('iteration #', iter, ':', user)
        if iter%100 == 0:
            end_check = timer()
            print('Durée depuis le debut :', round((end_check - start_check)/60,1), 'min')
            print('Petite pause de 1 min...')
            time.sleep(60)

        try:
            start = timer()
            #profile = api.get_user(user, count=n_vid)  # get user profile
            tries=0
            while tries<=1:
                try:
                    profile = api.by_username(user, count = n_vid)
                except Exception:
                    print('retry...')
                    tries+=1
                    continue
                break

            end = timer()
            print('temps execution:', round(end - start, 1), 's')

            if profile:  # check empty profile

                res = dict.fromkeys(col_df)


                prof = profile[0]['author']
                stat = profile[0]['authorStats']
                time_stamp = int(profile[0]['createTime'])

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

                start = timer()

                # get profile info
                res['signature'] = prof['signature']
                res['user_name'] = prof['uniqueId']
                res['nickname'] = prof['nickname']

                # get stats
                res['following_count'] = stat['followingCount']
                res['likes_count'] = stat['heartCount']
                res['video_count'] = stat['videoCount']
                res['last_active'] = datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')

                # get collab and hashtags
                #if n_vid > 6:
                #profile = api.by_username(user, count = n_vid)
                tiktoks = profile

                mentions, duos, collab, hashtag = [], [], [], []
                collab_url = {}
                if tiktoks:
                    for tiktok in tiktoks:
                        if 'textExtra' in tiktok:  # get special text
                            if only_duo:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                if (any([any(m in w for w in key_hashtag) for m in hashtag_cand])):
                                    collab_cand = list(filter(None, [text['userUniqueId'] for text in tiktok['textExtra']]))
                                    for collab_c in collab_cand:
                                        if collab_c not in collab:
                                            collab.append(collab_c)  # add collaborative artist
                                            collab_url[collab_c] = tiktok['video']['downloadAddr']
                                            if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                                duos.append(collab_c)
                                            else:
                                                mentions.append(collab_c)

                                    for hashtag_c in hashtag_cand:
                                        if hashtag_c not in hashtag:
                                            hashtag.append(hashtag_c)  # add hashtag used
                            else:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                collab_cand = list(filter(None, [text['userUniqueId'] for text in tiktok['textExtra']]))
                                for collab_c in collab_cand:
                                    if collab_c not in collab:
                                        collab.append(collab_c)  # add collaborative artist
                                        collab_url[collab_c] = tiktok['video']['downloadAddr']
                                        if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                            duos.append(collab_c)
                                        else:
                                            mentions.append(collab_c)

                                for hashtag_c in hashtag_cand:
                                    if hashtag_c not in hashtag:
                                        hashtag.append(hashtag_c)  # add hashtag used


                # musician filter
                if hashtag_filter:
                    if not (any([any(m in w for w in key_hashtag) for m in hashtag])):
                        continue

                # instrument and style
                inst, styl = [], []
                for s in style:
                    if s in hashtag:
                        styl.append(s)
                for i in instrument:
                    if i in hashtag:
                        inst.append(i)

                # complete profile info
                res['hashtags'] = hashtag
                res['collabs'] = collab
                res['duos'] = duos
                res['mentions'] = mentions
                res['collabs_url'] = collab_url
                res['instruments'] = inst
                res['styles'] = styl

                obj.writerow(tuple(res.values()))

                i_user += 1
                print('taille base de données :', i_user)
                print('liste des utilisateurs mentionnés de', user, ':')
                for c in collab_url.keys():
                    print(c, ':', str('https://tiktok.com/@'+c))

            for cand in collab:
                if cand not in users:
                    users.append(cand)

            if i_user >= n_user:
                print("\n Nombre d'utilisateurs voulu atteint")
                file.close()
                return

        except KeyboardInterrupt:
            file.close()
            print ('KeyboardInterrupt : interruption prématurée')
            return


        except:
            print("\n Erreur avec l'utilisateur :", user)

    if n_vid > 5 and i_user < 5:
        print("Il y a un nombre très faible d'utilisateurs : modifiez les paramètres d'entrée")

    file.close()
    print("Plus d'utilisateurs sur lesquels itérer")
    return


if __name__ == '__main__':

    typewrite('1')
    depart = int(input("Nombre d'utilisateurs avec lequel initialiser :"))

    print('Nom(s) de(s) utilisateurs(s) voulu(s) pour initialiser :')
    ini_list = []
    for i in range(depart):
        us = input()
        ini_list.append(us)

    typewrite('10')
    arret = int(input("Nombre d'utilisateurs avec lequel terminer l'algortihme: "))

    print('\n')
    print('Paramètres initiaux :')
    typewrite('30')
    n_vid = int(input("Nombre de TikToks max étudiés par profil (n_vid): "))
    typewrite('100000')
    max_followers = int(input("Nombre de followers max par profil (max_followers): "))
    typewrite(str(key_hashtag).replace("'", "")[1:-1])
    list_hashtags = str(input("Liste des hashtags pour le filtre (list_hashtags): "))
    list_hashtags = list_hashtags.split(',')
    tiktok(n_user=arret, seed=ini_list, n_vid=n_vid, list_hashtags=list_hashtags)

    # pruning : keep only musicians
    name_file = ini_list[0] + '_' + str(arret) + '_music.csv'
    data = pd.read_csv(name_file)
    music_collabs_url = []
    music_collabs = []
    for i in range(len(data)):
        collabs_url_dic = {}
        collabs_url_l = []
        for cand in (ast.literal_eval(data.collabs_url[i])):
            if cand in list(data.user_name):
                collabs_url_dic[cand] = ast.literal_eval(data.collabs_url[i])[cand]
                collabs_url_l.append(cand)
        music_collabs_url.append(collabs_url_dic)
        music_collabs.append(collabs_url_l)
    data.insert(12, 'music_collabs', music_collabs)
    data.insert(13, 'music_collabs_url', music_collabs_url)

    data.to_csv(name_file, index=False)

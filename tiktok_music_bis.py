from TikTokApi import TikTokApi
from timeit import default_timer as timer
import csv
from datetime import datetime
import time
import sys
import ast
import pandas as pd

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
                    music_collabs (list of str): list of username and urls of musicians with whom the user has collaborated
                    hashtags (list of str): list of unique hashtags used by user
                    styles (list of str): list of styles cited by user
                    instruments (list of str): list of instruments cited by user
    """
    # initialize control variables
    iter = 0
    i_user = 0
    pause = 0

    # users = seed
    # initialize : contour by_username problem
    users = [api.get_tiktok_by_url(s) for s in seed]
    info_init = [u['itemInfo']['itemStruct']['author'] for u in users]
    users = [[info['uniqueId'], info['id'], info['secUid']] for info in info_init]

    # list of key words for duos
    duo_list = ['duo', 'duet', 'duetme', 'duetwithme', 'duetthis', 'duets', 'duos']

    # list of key words for style and instruments
    style = ['jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
                'groove', 'classical', 'neosoul', 'indiemusic', 'lofi',
                'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro']
    instrument = ['guitar', 'bass', 'piano', 'drums', 'synth', 'rhodes',
                    'tuba', 'chords', 'saxophone', 'violin', 'flute', 'cello']

    # initialize csv doc
    name_file =  users[0][0] + '_' + str(n_user) + '_music.csv'
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
        print('iteration #', iter, ':', user[0])
        if iter%100 == 0:
            end_check = timer()
            print('Durée depuis le debut :', round((end_check - start_check)/60,1), 'min')
            print('Petite pause de 1 min...')
            time.sleep(60)

        try:
            # profile = api.get_user(user)  # get user profile
            start = timer()
            profile = api.user_posts(user[1], user[2], count=n_vid)
            end = timer()
            print('temps execution:', round(end - start, 1), 's')

            if profile:  # check empty profile

                res = dict.fromkeys(col_df)

                # prof = profile['userInfo']['user']
                prof = profile[0]['author']
                # stat = profile['userInfo']['stats']
                stat = profile[0]['authorStats']
                # tiktoks = profile['items']
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
                tiktoks = profile

                mentions, duos, collab, hashtag = [], [], [], []
                collab_url = {}
                if tiktoks:
                    for tiktok in tiktoks:
                        tiktok_id = tiktok['id']
                        if 'textExtra' in tiktok:  # get special text
                            if only_duo:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                if (any([any(m in w for w in hashtag_cand) for m in duo_list])):
                                    # collab_cand = list(filter(None, [text['userUniqueId'] for text in tiktok['textExtra']]))
                                    collab_cand = []
                                    for text in tiktok['textExtra']:
                                        if text['userUniqueId'] != '':
                                            collab_cand.append([text['userUniqueId'], text['userId'], text['secUid']])

                                    for collab_c in collab_cand:
                                        if collab_c not in collab:
                                            collab.append(collab_c)  # add collaborative artist
                                            collab_url[collab_c[0]] = str('https://tiktok.com/@'+user[0]+'/video/'+tiktok_id)
                                            if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                                duos.append(collab_c)
                                            else:
                                                mentions.append(collab_c)

                                    for hashtag_c in hashtag_cand:
                                        if hashtag_c not in hashtag:
                                            hashtag.append(hashtag_c)  # add hashtag used
                            else:
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                # collab_cand = list(filter(None, [text['userUniqueId'] for text in tiktok['textExtra']]))
                                collab_cand = []
                                for text in tiktok['textExtra']:
                                    if text['userUniqueId'] != '':
                                        collab_cand.append([text['userUniqueId'], text['userId'], text['secUid']])

                                for collab_c in collab_cand:
                                    if collab_c not in collab:
                                        collab.append(collab_c)  # add collaborative artist
                                        collab_url[collab_c[0]] = str('https://tiktok.com/@'+user[0]+'/video/'+tiktok_id)
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
                res['hashtags'] = hashtag[:25]
                res['collabs'] = [us[0] for us in collab]  # replace by collab
                res['duos'] = [us[0] for us in duos]  # replace by duos
                res['mentions'] = [us[0] for us in mentions]  # replace by mentions
                res['collabs_url'] = collab_url
                res['instruments'] = inst
                res['styles'] = styl

                obj.writerow(tuple(res.values()))

                i_user += 1
                print('taille base de données :', i_user)
                print('liste des utilisateurs mentionnés de', user[0], ':')  # replace by user
                for c in collab_url.keys():
                    print(c, ':', collab_url[c])

            for cand in collab:
                if cand not in users:
                    users.append(cand)

            if i_user >= n_user:
                print("\n")
                print("Nombre d'utilisateurs voulu atteint")
                file.close()
                return

        except KeyboardInterrupt:
            file.close()
            print ('KeyboardInterrupt : interruption prématurée')
            return


        except:
            print("\n")
            print("Erreur avec l'utilisateur :", user)

    if n_vid > 5 and i_user < 5:
        print("Il y a un nombre très faible d'utilisateurs : modifiez les paramètres d'entrée")

    file.close()
    print("Plus d'utilisateurs sur lesquels itérer")
    return


if __name__ == '__main__':

    # choose inputs
    print("Pour chaque étape, appuyez sur 'enter' pour valider les valeurs par défaut")
    depart = int(input("Nombre d'utilisateurs avec lequel initialiser (start = 1): ") or 1)

    print("Liens URL de(s) TikTok(s) des utilisateurs(s) voulu(s) pour initialiser l'algorithme: ")
    ini_list = []
    for i in range(depart):
        us = input()
        ini_list.append(us)

    arret = int(input("Nombre d'utilisateurs avec lequel terminer l'algortihme (n_user = 10): ") or 10)

    # show default parameters
    print('\n')
    print('Paramètres initiaux :')
    print("Nombre de TikToks max étudiés par profil: n_vid = 30")
    print("Nombre de followers max par profil: max_followers = 100000")
    print("Conservé uniquement les profils vérifiés ?: only_unverified=False")
    print("Conservé uniquement les relations via duo ?: only_duo=False")

    # modification of default parameters
    ask = str(input("Souhaitez vous gardez ces paramètres ? (tapez 'oui'/'enter' ou 'non'): ") or 'oui')
    if ask == 'oui':
        tiktok(n_user=arret, seed=ini_list)
    elif ask == 'non':
        print("Tapez les paramètres à modifier (enter si vous voulez garder la valeur par défaut)")
        n_vid = int(input("Nombre de TikToks max étudiés par profil (n_vid): ") or 30)
        max_followers = int(input("Nombre de followers max par profil (max_followers): ") or 100000)
        only_u = bool(input("Conservé uniquement les profils vérifiés ? (only_unverified=False): ") or False )
        only_d = bool(input("Conservé uniquement les relations via duo ? (only_duo=False): ") or False )
        tiktok(n_user=arret, seed=ini_list, n_vid=n_vid,
               only_unverified=only_u, only_duo=only_d)
    else:
        print('erreur')

    # pruning : keep only musicians
    username = ini_list[0].split('@')[1].split('/')[0]
    name_file = str(username) + '_' + str(arret) + '_music.csv'
    data = pd.read_csv(name_file)
    music_collabs = []
    for i in range(len(data)):
        music_collabs_u = ''
        for cand in (ast.literal_eval(data.collabs[i])):
            if cand in list(data.user_name):
                music_collabs_u+= str(cand)+' : '+str(ast.literal_eval(data.collabs_url[i])[cand])+'\n'
        music_collabs.append(music_collabs_u)
    data.insert(12, 'music_collabs', music_collabs)
    data = data.drop(columns='collabs_url')

    # convert format for visualisation
    data['mentions'] = data['mentions'].apply(lambda x: ast.literal_eval(str(x)))
    data['duos'] = data['duos'].apply(lambda x: ast.literal_eval(str(x)))
    data['collabs'] = data['collabs'].apply(lambda x: ast.literal_eval(str(x)))
    data['mentions'] = data['mentions'].apply(lambda x: ast.literal_eval(str(x)))
    data['hashtags'] = data['hashtags'].apply(lambda x: ast.literal_eval(str(x)))
    data['instruments'] = data['instruments'].apply(lambda x: ast.literal_eval(str(x)))
    data['styles'] = data['styles'].apply(lambda x: ast.literal_eval(str(x)))

    data['mentions'] = data['mentions'].apply('\n'.join)
    data['duos'] = data['duos'].apply('\n'.join)
    data['collabs'] = data['collabs'].apply('\n'.join)
    data['hashtags'] = data['hashtags'].apply(', '.join)
    data['instruments'] = data['instruments'].apply(', '.join)
    data['styles'] = data['styles'].apply(', '.join)

    data.to_csv(name_file, index=False)
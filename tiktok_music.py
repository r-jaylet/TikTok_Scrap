from TikTokApi import TikTokApi
from timeit import default_timer as timer
import csv
from datetime import datetime
import ast
import pandas as pd
import time

# list of key words for filters
style = ['jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie', 'groove', 'classical', 'neosoul',
         'indiemusic', 'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro']
instrument = ['guitar', 'bass', 'piano', 'drums', 'tuba', 'chords', 'saxophone', 'violin', 'flute', 'cello']
key_hashtag = ['music', 'musician', 'instrumentalist', 'impro', 'solo', 'band', 'newmusic', 'musiciansoftiktok',
               'songwriter', 'rythm', 'cover', 'jazztok', 'producer', 'guitarsolo']

#verifyFp = ''
#api = TikTokApi(custom_verify_fp=verifyFp)
#ms_token = "VgsxC2tZxqdQyDO6969jXRphOBdIfBNoGLvIfUmMBt5TZLCmpx5RJyaeCrONHMjeP1bWVXuSkdOqxGBFVCYoq39J5QHrCN8QG5r9_dB3xFHAaLk4fCaRLs-XMkRuFcFORz5AFLloXNw="
#api = TikTokApi(ms_token=ms_token)
api = TikTokApi()

def tiktok_function(only_unverified=True,
                    only_duo=False,
                    n_user=10,
                    n_vid=30,
                    max_followers=100000,
                    graph_direction=True,
                    seed=None):
    """
    Creates a dataframe of musicians' profile on TikTok.
            Parameters:
                only_unverified (bool): if 'True', only select unverified profiles
                only_duo (bool): if 'True', only select duet connections
                n_user (int): number of artists wanted in the database
                n_vid (int): number of TikToks scrapped in each profile
                max_followers (int): maximum number of followers
                graph_direction (bool): if 'True', select 'in' collabs, else select 'out' collabs
                seed (list of str): list of users to initiate reccursive algorithm
            Returns:
                user_db (csv): datebase of users with its different characteristics
                    user_name (str): unique username of profile
                    signature (str): bio description of profile
                    verified (bool): is the user verified or not
                    basic_stats (str) : statistics (follower, following, likes, video, last_active, freq_post)
                    collabs (str): list of username with whom the user has collaborated
                    music_collabs (str): list of musicians with whom the user has collaborated
                    hashtags (str): list of unique hashtags used by user seperated by general, style, instrument
    """

    # initialize control variables
    iter = 0
    i_user = 0

    # users = seed
    users = [api.user(username=s).username for s in seed]

    # list of key words for duos
    duo_list = ['duo', 'duet', 'duetme', 'duetwithme', 'duetthis', 'duets', 'duos']

    list_hashtags = key_hashtag + style + instrument

    # initialize csv doc
    name_file = users[0] + '_' + str(n_user) + '_music.csv'
    file = open(name_file, 'w', encoding='utf-8')
    obj = csv.writer(file)
    col_db = ['user_name', 'signature', 'verified', 'basic_stats', 'collabs', 'collabs_url', 'hashtags']
    obj.writerow(col_db)

    for user in users:

        iter += 1
        print('\n')
        print('iteration #', iter, ':', user)

        try:
            start = timer()
            user_profile = api.user(username=user)
            time.sleep(1)
            profile = user_profile.info_full()
            end = timer()
            print("Temps recherche du profil:", round(end - start, 1), 's')

            if profile:  # check empty profile

                # get basic info
                res = dict.fromkeys(col_db)
                prof = profile['user']
                stat = profile['stats']
                time_stamp = int(profile['user']['createTime'])

                # check filters
                if only_unverified:
                    if prof['verified']:
                        print("Le profil n'est pas ajouté car l'utilisateur est 'vérifié'")
                        continue
                    else:
                        res['verified'] = prof['verified']
                else:
                    res['verified'] = prof['verified']

                # get unique profile info
                res['signature'] = prof['signature']
                res['user_name'] = prof['uniqueId']

                # get stats
                basic_stats = {}
                if stat['followerCount'] > max_followers:
                    print("Le profil n'est pas ajouté car "
                          "l'utilisateur a trop d'abonnés (" + str(stat['followerCount']) + " abonnés)")
                    continue
                else:
                    basic_stats['follower_count'] = stat['followerCount']

                # get videos
                start = timer()
                tiktoks = [vid.as_dict for vid in user_profile.videos(count=n_vid)]
                end = timer()
                print("Temps recherche des vidéos:", round(end - start, 1), 's')

                basic_stats['following_count'] = stat['followingCount']
                basic_stats['likes_count'] = stat['heartCount']
                basic_stats['video_count'] = stat['videoCount']
                basic_stats['last_active'] = datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')
                date = [datetime.utcfromtimestamp(int(tiktoks[t]['createTime'])).strftime('%Y-%m-%d')
                        for t in range(len(tiktoks))]
                dates = [datetime.strptime(d, "%Y-%m-%d") for d in date]
                delta = [abs((dates[d + 1] - dates[d]).days) for d in range(len(dates)-1)]
                freq = int(sum(delta) / len(delta))
                if freq == 0:
                    freq = 1
                basic_stats['freq_post'] = str(freq) + ' days'
                res['basic_stats'] = basic_stats

                if graph_direction:  # select 'a mentionné ...' link

                    # get collabs and hashtags
                    mentions, duos, collab, hashtag = [], [], [], []
                    collab_url = {}
                    all_hashtags = []
                    if tiktoks:  # check videos existence
                        for tik_num, tiktok in enumerate(tiktoks):
                            tiktok_id = tiktok['id']
                            if 'textExtra' in tiktok:  # get special text
                                if only_duo:
                                    hashtag_cand = list(filter(None, [text['hashtagName']
                                                                      for text in tiktok['textExtra']]))
                                    if not (any([any(m in w for w in hashtag_cand) for m in duo_list])):
                                        continue
                                    else:
                                        collab_cand = list(filter(None, [text['userUniqueId']
                                                                         for text in tiktok['textExtra']]))
                                        for collab_c in collab_cand:
                                            if collab_c not in collab:
                                                collab.append(collab_c)  # add collaborative artist
                                                collab_url[collab_c] = str(
                                                    'https://tiktok.com/@' + user + '/video/' + tiktok_id)
                                                if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                                    duos.append(collab_c)
                                                    collab_url[collab_c] += ' (duo, vidéo num:' + str(tik_num) + ')'
                                                else:
                                                    mentions.append(collab_c)
                                                    collab_url[collab_c] += ' (mention, vidéo num:' + str(tik_num) + ')'

                                        all_hashtags += hashtag_cand

                                        for hashtag_c in hashtag_cand:
                                            if hashtag_c not in hashtag:
                                                hashtag.append(hashtag_c)  # add hashtag used
                                else:
                                    hashtag_cand = list(filter(None, [text['hashtagName']
                                                                      for text in tiktok['textExtra']]))
                                    collab_cand = list(filter(None, [text['userUniqueId']
                                                                     for text in tiktok['textExtra']]))
                                    for collab_c in collab_cand:
                                        if collab_c not in collab:
                                            collab.append(collab_c)  # add collaborative artist
                                            collab_url[collab_c] = str(
                                                'https://tiktok.com/@' + user + '/video/' + tiktok_id)
                                            if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                                duos.append(collab_c)
                                                collab_url[collab_c] += ' (duo, vidéo num: ' + str(tik_num) + ')'
                                            else:
                                                mentions.append(collab_c)
                                                collab_url[collab_c] += ' (mention, vidéo num: ' + str(tik_num) + ')'

                                    all_hashtags += hashtag_cand

                                    for hashtag_c in hashtag_cand:
                                        if hashtag_c not in hashtag:
                                            hashtag.append(hashtag_c)  # add hashtag used

                else:  # select 'mentionné par ...' link

                    # get hashtags
                    hashtag = []
                    all_hashtags = []
                    if tiktoks:  # check videos existence
                        for tik_num, tiktok in enumerate(tiktoks):
                            tiktok_id = tiktok['id']
                            if 'textExtra' in tiktok:  # get special text
                                hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                                all_hashtags += hashtag_cand

                                for hashtag_c in hashtag_cand:
                                    if hashtag_c not in hashtag:
                                        hashtag.append(hashtag_c)  # add hashtag used

                    # get collabs
                    mentions, duos, collab = [], [], []
                    tiktok_out = api.search.videos(user)

                    for video in tiktok_out:
                        tik_out = video.as_dict
                        if (tik_out['author']['uniqueId'] != user) & (tik_out['author']['verified'] != only_unverified)\
                                & (tik_out['authorStats']['followerCount'] < max_followers):

                            collab_c = str(tik_out['author']['uniqueId'])
                            if 'textExtra' in tik_out:  # get special text
                                if only_duo:
                                    hashtag_cand = list(filter(None, [text['hashtagName']
                                                                      for text in tik_out['textExtra']]))
                                    if not (any([any(m in w for w in hashtag_cand) for m in duo_list])):
                                        continue
                                    else:
                                        if collab_c not in collab:
                                            collab.append(collab_c)  # add collaborative artist
                                            collab_url[collab_c] = str(
                                                'https://tiktok.com/@' + collab_c + '/video/' + tik_out['id'])
                                            if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                                duos.append(collab_c)
                                                collab_url[collab_c] += ' (duo)'
                                            else:
                                                mentions.append(collab_c)
                                                collab_url[collab_c] += ' (mention)'
                                else:
                                    if collab_c not in collab:
                                        collab.append(collab_c)  # add collaborative artist
                                        collab_url[collab_c] = str(
                                            'https://tiktok.com/@' + collab_c + '/video/' + tik_out['id'])
                                        if any([any(m in w for w in hashtag_cand) for m in duo_list]):
                                            duos.append(collab_c)
                                            collab_url[collab_c] += ' (duo)'
                                        else:
                                            mentions.append(collab_c)
                                            collab_url[collab_c] += ' (mention)'

                inst_count = dict.fromkeys(instrument, 0)
                styl_count = dict.fromkeys(style, 0)
                for hashtag_c in all_hashtags:
                    if hashtag_c in instrument:
                        inst_count[hashtag_c] += 1
                    if hashtag_c in style:
                        styl_count[hashtag_c] += 1

                # musician filter
                if not (any([any(m in w for w in list_hashtags) for m in hashtag])):
                    print("Le profil n'est pas ajouté car il n'est pas considéré comme un musicien")
                    continue

                # hashtags by category
                inst, styl, has = [], [], []
                for i in instrument:
                    if inst_count[i] != 0:
                        inst_num = str(i) + ' (' + str(inst_count[i]) + ')'
                        inst.append(inst_num)
                for s in style:
                    if styl_count[s] != 0:
                        styl_num = str(s) + ' (' + str(styl_count[s]) + ')'
                        styl.append(styl_num)
                for h in hashtag[:20]:
                    if (h not in styl) and (h not in inst):
                        has.append(h)

                hashtag_cat = {}
                hashtag_cat['instruments'] = inst
                hashtag_cat['styles'] = styl
                hashtag_cat['others'] = has

                # complete profile info
                res['hashtags'] = hashtag_cat
                res['collabs'] = duos + mentions
                res['collabs_url'] = collab_url

                # add profile in database
                obj.writerow(tuple(res.values()))

                i_user += 1
                print('Taille base de données :', i_user)
                print('Liste des utilisateurs mentionnés de', user, ':')
                for c in collab_url.keys():
                    print(c, ':', collab_url[c])

            for cand_collab in collab:
                if cand_collab not in users:
                    users.append(cand_collab)

            if i_user >= n_user:
                print("\n")
                print("Le nombre d'utilisateurs voulu est atteint")
                file.close()
                return

        except KeyboardInterrupt:
            file.close()
            print('KeyboardInterrupt : interruption prématurée')
            return

        except:
            print("\n")
            print("Erreur avec l'utilisateur :", user)

    file.close()
    print("il n'y a plus d'utilisateurs sur lesquels itérer")
    return


if __name__ == '__main__':

    # choose inputs
    print("Pour chaque étape, appuyez sur 'enter' pour valider les valeurs par défaut (valeur entre parenthèses)")
    print('\n')
    print('Paramètres initiaux :')
    depart = int(input("Nombre d'utilisateurs avec lequel initialiser (start = 1): ") or 1)
    print("Username(s) des utilisateurs(s) voulu(s) pour initialiser l'algorithme: ")
    ini_list = []
    for i in range(depart):
        us = input()
        ini_list.append(us)
    arret = int(input("Nombre d'utilisateurs avec lequel terminer l'algortihme (n_user = 10): ") or 10)
    n_v = int(input("Nombre de TikToks max étudiés par profil (n_vid = 30): ") or 30)
    m_f = int(input("Nombre de followers max par profil (max_followers = 100000): ") or 100000)
    o_u = bool(input("Conserver uniquement les profils pas vérifiés ? (only_unverified=True): ") or True)
    o_d = bool(input("Conserver uniquement les relations via duo ? (only_duo=False): ") or False)
    g_d = bool(input("Direction de recherche - 'à mentionné ...' -> True /"
                     " 'mentionné par ...' -> False (graph_direction=True): ") or True)

    # call function with defined parameters
    tiktok_function(n_user=arret,
                    seed=ini_list,
                    n_vid=n_v,
                    max_followers=m_f,
                    only_unverified=o_u,
                    only_duo=o_d,
                    graph_direction=g_d)

    # pruning : keep only musicians in output database
    name_file = str(ini_list[0]) + '_' + str(arret) + '_music.csv'
    data = pd.read_csv(name_file)
    music_collabs = []
    for i in range(len(data)):
        music_collabs_u = ''
        for cand in (ast.literal_eval(data.collabs[i])):
            if cand in list(data.user_name):
                music_collabs_u += str(cand) + ' : ' + str(ast.literal_eval(data.collabs_url[i])[cand]) + '\n'
        music_collabs.append(music_collabs_u)
    data.insert(6, 'music_collabs', music_collabs)
    data = data.drop(columns='collabs_url')

    # convert format for visualisation
    data['collabs'] = data['collabs'].apply(lambda x: ast.literal_eval(str(x)))
    data['collabs'] = data['collabs'].apply('\n'.join)
    stats = []
    hashs = []
    for i in range(len(data)):
        stat_to_str = ''
        hash_to_str = ''
        stat = ast.literal_eval(data.basic_stats[i])
        has = ast.literal_eval(data.hashtags[i])
        for j in range(len(stat)):
            stat_to_str += str(list(stat.keys())[j]) + ' : ' + str(list(stat.values())[j]) + '\n'
        stats.append(stat_to_str)
        for j in range(len(has)):
            hash_to_str += str(list(has.keys())[j]) + ' : ' + ', '.join(str(x) for x in list(has.values())[j]) + '\n'
        hashs.append(hash_to_str)
    data['basic_stats'] = stats
    data['hashtags'] = hashs
    data.to_csv(name_file, index=False)

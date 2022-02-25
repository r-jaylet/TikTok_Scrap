from TikTokApi import TikTokApi
from timeit import default_timer as timer
from datetime import datetime
import pandas as pd

verifyFp = ''

api = TikTokApi(custom_verify_fp=verifyFp)


def tiktok_hashtag(only_unverified=True,
                   n_tiktok_max=1000,
                   max_followers=10000,
                   hashtag_start='synthsolo'):
    """
    Creates a dataframe of musicians' video on TikTok from a given challenge's page
            Parameters:
                only_unverified (bool): if 'True', only select unverified profiles
                n_tiktok_max (int): number tiktoks studied
                max_followers (int): maximum number of followers
                hashtag_start (str): hashtags or challenges to search for
            Returns:
                user_db (csv): datebase of users with its different characteristics
                    user_name (str): unique username of video
                    signature (str): bio description of video
                    verified (bool): is the user verified or not
                    basic_stats (str) : stats (follower_count, following_count, likes_count, video_count, last_active)
                    hashtags (str) : list of hashtags used in videos
    """
    # initialize control variables
    iter = 0

    # initialize dataframe
    col_db = ['user_name', 'signature', 'verified', 'basic_stats', 'links', 'hashtags']
    user_df = pd.DataFrame(columns=col_db)

    start = timer()
    tag = api.hashtag(name=hashtag_start)
    tiktoks = [video.as_dict for video in tag.videos(count=n_tiktok_max)]

    end = timer()
    print("Temps d'exécution de la recherche pour", hashtag_start, ":", round(end - start, 1), 's')
    print('Nombre de vidéos à traiter :', len(tiktoks))

    for tik_num, tiktok in enumerate(tiktoks):

        iter += 1

        try:
            video = tiktoks[tik_num]

            if video:  # check empty video

                res = dict.fromkeys(col_db)
                prof = video['author']
                stat = video['authorStats']
                time_stamp = int(video['createTime'])

                # check filters
                if only_unverified:
                    if prof['verified']:
                        continue
                    else:
                        res['verified'] = prof['verified']
                else:
                    res['verified'] = prof['verified']

                # get video info
                if prof['uniqueId'] in list(user_df.user_name):
                    update = user_df.loc[user_df.user_name == prof['uniqueId'], 'links'] +\
                             '\n' + 'https://tiktok.com/@' + prof['uniqueId'] + '/video/' + video['id']
                    user_df.loc[user_df.user_name == prof['uniqueId'], 'links'] = update
                    hash_list = user_df.loc[user_df.user_name == prof['uniqueId'], 'hashtags'].tolist()[0]
                    if 'textExtra' in video:
                        hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                        for hashtag_c in hashtag_cand:
                            if hashtag_c not in hash_list:
                                hash_list.append(hashtag_c)  # add hashtag used
                    res['hashtags'] = hash_list
                    continue
                else:
                    res['user_name'] = prof['uniqueId']

                res['signature'] = prof['signature']
                res['user_name'] = prof['uniqueId']

                # get stats
                basic_stats = {}
                if stat['followerCount'] > max_followers:
                    continue
                else:
                    basic_stats['follower_count'] = stat['followerCount']

                basic_stats['following_count'] = stat['followingCount']
                basic_stats['likes_count'] = stat['heartCount']
                basic_stats['video_count'] = stat['videoCount']
                basic_stats['last_active'] = datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')
                res['basic_stats'] = basic_stats

                res['links'] = 'https://tiktok.com/@' + prof['uniqueId'] + '/video/' + video['id']
                hash_list = hashtag_start.split()
                if 'textExtra' in video:
                    hashtag_cand = list(filter(None, [text['hashtagName'] for text in tiktok['textExtra']]))
                    for hashtag_c in hashtag_cand:
                        if hashtag_c not in hash_list:
                            hash_list.append(hashtag_c)  # add hashtag used
                res['hashtags'] = hash_list

                # add profile in database
                user_df = user_df.append(res, ignore_index=True)  # update dataframe

        except:
            print("\n")
            print("Erreur avec l'utilisateur :", prof['uniqueId'])

    stats = []
    hashs = []
    for i in range(len(user_df)):
        stat_to_str = ''
        stat = user_df.basic_stats[i]
        hash_to_str = ', '.join(user_df.hashtags[i])
        hashs.append(hash_to_str)
        for j in range(len(stat)):
            stat_to_str += str(list(stat.keys())[j]) + ' : ' + str(list(stat.values())[j]) + '\n'
        stats.append(stat_to_str)
    user_df['basic_stats'] = stats
    user_df['hashtags'] = hashs

    name_file = str(hashtag_start).replace(' ', '_') + '_music_by_hashtag.csv'
    user_df.to_csv(name_file, index=False)

    return


if __name__ == '__main__':

    # choose inputs
    print("Pour chaque étape, appuyez sur 'enter' pour valider les valeurs par défaut (valeur entre parenthèses)")
    print('\n')
    print('Paramètres initiaux :')
    depart = str(input("Hashtags avec lequel initialiser ('synthsolo' par défaut): ") or 'synthsolo')
    o_u = bool(input("Conserver uniquement les profils pas vérifiés ? (only_unverified=True): ") or True)
    n_t = int(input("Nombre de videos à vouloir être traiter (n_tiktok_max = 1000): ") or 1000)
    m_f = int(input("Nombre de followers max par profil (max_followers = 10000): ") or 10000)

    # call function with defined parameters
    tiktok_hashtag(only_unverified=o_u,
                   n_tiktok_max=n_t,
                   max_followers=m_f,
                   hashtag_start=depart)

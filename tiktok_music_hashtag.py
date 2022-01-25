from TikTokApi import TikTokApi
from timeit import default_timer as timer
from datetime import datetime
import pandas as pd

verifyFp = ''

api = TikTokApi.get_instance(custom_verifyFp=verifyFp, use_test_endponts=True)


def tiktok(only_unverified=True,
           n_tiktok=1000,
           max_followers=10000,
           hashtag='synthsolo'):
    """
    Creates a dataframe of musicians' profile on TikTok from a given challenge's page
            Parameters:
                only_unverified (bool): if 'True', only select unverified profiles
                n_tiktok (int): number tiktoks studied
                max_followers (int): maximum number of followers
                hashtag (str): hashtag or challenge to search for
            Returns:
                user_db (csv): datebase of users with its different characteristics
                    user_name (str): unique username of profile
                    signature (str): bio description of profile
                    verified (bool): is the user verified or not
                    basic_stats (str) : statistics (follower_count, following_count, likes_count, video_count, last_active, freq_post)
    """
    # initialize control variables
    iter = 0

    # users = seed
    users = []

    # initialize dataframe
    col_db = ['user_name', 'signature', 'verified', 'basic_stats', 'collabs']
    user_df = pd.DataFrame(columns=col_db)

    start = timer()
    tiktoks = api.by_hashtag(hashtag, count=n_tiktok)
    end = timer()
    print("Temps d'exécution de la recherche:", round(end - start, 1), 's')

    for tik_num, tiktok in enumerate(tiktoks):

        iter += 1

        #try:
        profile = tiktoks[tik_num]

        if profile:  # check empty profile

            res = dict.fromkeys(col_db)

            prof = profile['author']
            stat = profile['authorStats']
            time_stamp = int(profile['createTime'])

            # check filters
            if only_unverified:
                if prof['verified']:
                    continue
                else:
                    res['verified'] = prof['verified']
            else:
                res['verified'] = prof['verified']

            # get profile info
            if prof['uniqueId'] not in user_df.username:
                continue
            else:
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
            basic_stats['date'] = datetime.utcfromtimestamp(time_stamp).strftime('%Y-%m-%d')

            # add profile in datebase
            user_df = user_df.append(res, ignore_index=True)  # update dataframe

        """
        except:
            print("\n")
            print("Erreur avec l'utilisateur :", prof['uniqueId'])
        """

    stats = []
    for i in range(len(user_df)):
        stat_to_str = ''
        stat = user_df.basic_stats[i]
        for j in range(len(stat)):
            stat_to_str += str(list(stat.keys())[j]) + ' : ' + str(list(stat.values())[j]) + '\n'
        stats.append(stat_to_str)
    user_df['basic_stats'] = stats

    name_file = str(hashtag) + '_' + str(n_tiktok) + '_music_by_hashtag.csv'
    user_df.to_csv(name_file, index=False)

    return


if __name__ == '__main__':

    # choose inputs
    print("Pour chaque étape, appuyez sur 'enter' pour valider les valeurs par défaut (valeur indiquée entre parenthèses)")
    print('\n')
    print('Paramètres initiaux :')
    depart = str(input("Hashtags avec lequel initialiser ('synthsolo' par défaut): ") or 'synthsolo')
    o_u = bool(input("Conserver uniquement les profils vérifiés ? (only_unverified=True): ") or True)
    n_t = int(input("Nombre de videos à vouloir être traiter (n_tiktok = 1000): ") or 1000)
    m_f = int(input("Nombre de followers max par profil (max_followers = 10000): ") or 10000)

    # call function with defined parameters
    tiktok(only_unverified=o_u,
           n_tiktok=n_t,
           max_followers=10000,
           hashtag=depart)

import pandas as pd


def filter_tiktok(file_name='',
                  only_unverified=False,
                  only_duo=False,
                  only_mention=False,
                  hashtags='',
                  max_followers=100000):
    """
    Filter dataframe given by tiktok_music().py according to criterias.
            Parameters:
                file_name (str): file of database to filter
                only_unverified (bool): if 'True', only select unverified profiles
                only_duo (bool): if 'True', only select duet connections
                max_followers (int): maximum number of followers
                hashtags (str): list of hashtags to filter upon
            Returns:
                user_db (csv): datebase of filtered users with its different characteristics
    """
    data = pd.read_csv(file_name)
    data.reset_index(level=0, inplace=True)

    instruments = []
    styles = []
    others = []
    collabs_df = []
    music_collabs_df = []
    follower_count = []
    following_count = []
    likes_count = []
    video_count = []
    last_active = []
    freq_post = []

    for i in range(len(data)):
        hashtags_cat = str(data.hashtags[i]).split('\n')
        hashtags_cat.pop()
        hashtags_cat_words = [cat.split(': ')[1] for cat in hashtags_cat]
        instr_all = hashtags_cat_words[0].split(', ')
        if instr_all != [' ']:
            instr = [i.split(' (')[0] for i in instr_all]
        else:
            instr = ['None']
        sty_all = hashtags_cat_words[1].split(', ')
        if sty_all != [' ']:
            sty = [s.split(' (')[0] for s in sty_all]
        else:
            sty_count = [0]
        othe = hashtags_cat_words[2].split(', ')
        instruments.append(instr)
        styles.append(sty)
        others.append(othe)

        coll = str(data.collabs[i]).split("\n")
        coll.pop()
        collabs_df.append(coll)

        music_coll = str(data.music_collabs[i]).split("\n")
        music_coll.pop()
        music_collabs_df.append(music_coll)

        stats_cat = data.basic_stats[i].split("\n")
        stats_cat.pop()
        stats_cat_words = [cat.split(':')[1] for cat in stats_cat]
        follower_c = stats_cat_words[0]
        following_c = stats_cat_words[1]
        likes_c = stats_cat_words[2]
        video_c = stats_cat_words[3]
        last_a = stats_cat_words[4]
        freq_p = str(stats_cat_words[5]).replace(' days', '')
        follower_count.append(follower_c)
        following_count.append(following_c)
        likes_count.append(likes_c)
        video_count.append(video_c)
        last_active.append(last_a)
        freq_post.append(freq_p)

    data['instruments'] = instruments
    data['styles'] = styles
    data['others'] = others
    data['collabs_df'] = collabs_df
    data['music_collabs_df'] = music_collabs_df
    data['follower_count'] = follower_count
    data['following_count'] = following_count
    data['likes_count'] = likes_count
    data['video_count'] = video_count
    data['last_active'] = last_active
    data['freq_post'] = freq_post
    data[['follower_count', 'following_count', 'likes_count', 'video_count', 'freq_post']] = data[['follower_count', 'following_count', 'likes_count', 'video_count', 'freq_post']].apply(pd.to_numeric)

    # select according to criterias
    if only_unverified:
        data = data[data['verified'] == False]
    if only_duo:
        data.music_collabs_df = data.music_collabs_df.apply(lambda x: [a for a in x if '(duo,' in a])
        music_col = []
        for i in range(len(data)):
            music_collabs_u = ''
            for coll in data.music_collabs_df[i]:
                music_collabs_u += str(coll) + '\n'
            music_col.append(music_collabs_u)
        data['music_collabs'] = music_col
    if only_mention:
        data.music_collabs_df = data.music_collabs_df.apply(lambda x: [a for a in x if '(mention,' in a])
        music_col = []
        for i in range(len(data)):
            music_collabs_u = ''
            for coll in data.music_collabs_df[i]:
                music_collabs_u += str(coll) + '\n'
            music_col.append(music_collabs_u)
        data['music_collabs'] = music_col
    if max_followers != 10000:
        data = data[data['follower_count'] < max_followers]
    if hashtags != '':
        data['hash'] = data['instruments'] + data['styles'] + data['others']
        selection = hashtags.split(' ')
        mask = data.hash.apply(lambda x: any(item for item in selection if item in x))
        data = data[mask]


    data = data[['user_name', 'signature', 'verified', 'basic_stats', 'collabs', 'music_collabs', 'hashtags']]

    name = str(input("Nommer le fichier modifié " + "'" + file_name + "'" + "(ne pas ajouter .csv) : ") or file_name.split('.')[0]+'_filter')

    new_file_name = name + '.csv'
    data.to_csv(new_file_name, index=False)


if __name__ == '__main__':

    file_name = str(input("nom fichier : "))

    # choose inputs
    print("Pour chaque étape, appuyez sur 'enter' pour valider les valeurs par défaut (valeur indiquée entre parenthèses)")
    print('\n')
    print('Paramètres à filtrer :')
    max_f = int(input("Nombre de followers max par profil (max_followers = 100000): ") or 100000)
    o_u = bool(input("Conserver uniquement les profils vérifiés ? (only_unverified=False): ") or False)
    o_d = bool(input("Conserver uniquement les relations via duo ? (only_duo=False): ") or False)
    o_m = bool(input("Conserver uniquement les relations via mention ? (only_mention=False): ") or False)
    h = str(input("Conserver uniquement les utilisateurs ayant mentionnés les mots suivants (séparés les mots par un espace) : ") or '')

    # call function with defined parameters
    filter_tiktok(file_name=file_name,
                  hashtags=h,
                  max_followers=max_f,
                  only_unverified=o_u,
                  only_duo=o_d,
                  only_mention=o_m)

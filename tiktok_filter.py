from timeit import default_timer as timer
import csv
from datetime import datetime
import ast
import pandas as pd


def filter_tiktok(file_name='',
                  only_unverified=True,
                  only_duo=False,
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

    # reformat file

    # select according to criterias
    if only_unverified:
        print('unver')
    if only_duo:
        print('unver')
    if max_followers != 10000:
        print('unver')
    if hashtags != '':
        print('unver')

    name = str(input("Nommer le fichier " + "'" + file_name + "'" + "(ne pas ajouter .csv) : ") or file_name.split('.')[0]+'_filter.csv')
    data.to_csv(name, index=False)


if __name__ == '__main__':

    # choose inputs
    print("Pour chaque étape, appuyez sur 'enter' pour valider les valeurs par défaut (valeur indiquée entre parenthèses)")
    print('\n')
    print('Paramètres à filtrer :')
    m_f = int(input("Nombre de followers max par profil (max_followers = 100000): ") or 100000)
    o_u = bool(input("Conserver uniquement les profils vérifiés ? (only_unverified=True): ") or True)
    o_d = bool(input("Conserver uniquement les relations via duo ? (only_duo=False): ") or False)
    h = str(input("Conserver uniquement les utilisateurs ayant mentionnés les mots suivants (séparés les mots par un espace) ") or 'ze')

    # call function with defined parameters
    filter_tiktok(hashtags=h,
                  max_followers=m_f,
                  only_unverified=o_u,
                  only_duo=o_d)

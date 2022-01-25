import numpy as np
import pandas as pd


def convert_to_adjacency(data):
    adj_list = []
    for i in range(len(data)):
        user_collabs = str(data.music_collabs[i]).split("\n")
        user_collabs.pop()
        username_collabs = [u.split(" ")[0] for u in user_collabs]
        cand_list = [int(data[data['user_name'] == u].index.values) for u in username_collabs]
        adj_list.append(cand_list)
    return adj_list


def gephi(file):
    data = pd.read_csv(file)
    data.reset_index(level=0, inplace=True)

    style = ['jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
             'groove', 'classical', 'neosoul', 'indiemusic',
             'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro']
    instrument = ['guitar', 'bass', 'piano', 'drums',
                  'tuba', 'chords', 'saxophone', 'violin', 'flute', 'cello']

    res_style = np.zeros(21)
    res_instru = np.zeros(21)

    for i in range(len(data)):
        hashtags_cat = str(data.hashtags[i]).split("\n")
        hashtags_cat.pop()
        hashtags_cat_words = [cat.split(':')[1] for cat in hashtags_cat]
        instr = hashtags_cat_words[0].split(',')
        sty = hashtags_cat_words[1].split(',')
        l_style = np.array([int(any(m in w for w in sty)) for m in style])
        l_instru = np.array([int(any(m in w for w in instr)) for m in instrument])
        res_style = [int(x + y) for x, y in zip(res_style, l_style)]
        res_instru = [int(x + y) for x, y in zip(res_instru, l_instru)]

    tab_style = []
    tab_instrument = []

    for i in range(len(data)):
        style_bool = np.array([any(m in w for w in sty) for m in style])
        tab_s = [i for i, x in enumerate(style_bool) if x]
        if tab_s != []:
            tab_style.append(min(tab_s))
        else:
            tab_style.append(None)
        instrument_bool = np.array([any(m in w for w in instr) for m in instrument])
        tab_i = [i for i, x in enumerate(instrument_bool) if x]
        if tab_i != []:
            tab_instrument.append(min(tab_i))
        else:
            tab_instrument.append(None)

    tab_instrument_ = []
    for i in range(len(tab_instrument)):
        if tab_instrument[i] is not None:
            tab_instrument_.append(instrument[tab_instrument[i]])
        else:
            tab_instrument_.append('None')
    tab_style_ = []
    for i in range(len(tab_style)):
        if tab_style[i] is not None:
            tab_style_.append(style[tab_style[i]])
        else:
            tab_style_.append('None')
    data['instrument'] = tab_instrument_
    data['style'] = tab_style_

    nodes = data[['index', 'user_name', 'style', 'instrument']]
    nodes = nodes.rename(columns={'index': 'Id'})
    nodes = nodes.rename(columns={'user_name': 'Label'})

    edges = pd.DataFrame(columns=['Source', 'Target', 'Type'])
    for i, collab in enumerate(convert_to_adjacency(data)):
        if collab != []:
            for c in collab:
                series = pd.Series([i, c, 'undirected'], index=edges.columns)
                edges = edges.append(series, ignore_index=True)

    return nodes, edges


if __name__ == '__main__':

    file_name = str(input("nom fichier:"))
    output = gephi(file_name)
    file_name = file_name.split('.')[0] + '_gephi'
    file_name_nodes = file_name + '_nodes.csv'
    file_name_edges = file_name + '_edges.csv'

    output[0].to_csv(file_name_nodes, index=False)
    output[1].to_csv(file_name_edges, index=False)

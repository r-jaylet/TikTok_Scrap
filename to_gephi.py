import numpy as np
import pandas as pd
import ast


def convert_to_adjacency(data):
    L = []
    for i in range(len(data)):
        l = []
        for cand in (ast.literal_eval(data.collabs[i])):
            if cand in list(data.user_name):
                l.append(int(data[data['user_name'] == cand]['index']))
        L.append(l)
    return L


def gephi(file_name):
    data = pd.read_csv(file_name)
    data.reset_index(level=0, inplace=True)

    weight = [len(li) for li in convert_to_adjacency(data)]
    data['poids'] = weight

    style = ['jazz', 'funk', 'rock', 'pop', 'rap', 'metal', 'rnb', 'hiphop', 'indie',
            'groove', 'classical', 'neosoul', 'indiemusic',
            'blues', 'punk', 'folk', 'gospel', 'dubstep', 'house', 'electro']
    instrument =['guitar', 'bass', 'piano', 'drums',
                'tuba', 'chords', 'saxophone', 'violin', 'flute', 'cello']
    vocalist = ['sing', 'singer', 'singingchallenge']

    res_style = np.zeros(21)
    res_instru = np.zeros(21)

    for i in range(len(data)):
        L_style = np.array([int(any(m in w for w in ast.literal_eval(data.hashtags[i]))) for m in style])
        L_instru = np.array([int(any(m in w for w in ast.literal_eval(data.hashtags[i]))) for m in instrument])
        res_style = [int(x + y) for x, y in zip(res_style, L_style)]
        res_instru = [int(x + y) for x, y in zip(res_instru, L_instru)]

    style_count = dict.fromkeys(style)
    for i,sty in enumerate(style_count.keys()):
        style_count[sty] = res_style[i]
    style_count = dict(sorted(style_count.items(), key=lambda item: item[1]))

    instru_count = dict.fromkeys(instrument)
    for i,inst in enumerate(instru_count.keys()):
        instru_count[inst] = res_instru[i]
    instru_count = dict(sorted(instru_count.items(), key=lambda item: item[1]))

    tab_style = []
    tab_instrument = []

    for i in range(len(data)):
        style_bool = np.array([any(m in w for w in ast.literal_eval(data.hashtags[i])) for m in style])
        tab_s = [i for i, x in enumerate(style_bool) if x]
        if tab_s != []:
            tab_style.append(min(tab_s))
        else:
            tab_style.append(None)
        instrument_bool = np.array([any(m in w for w in ast.literal_eval(data.hashtags[i])) for m in instrument])
        tab_i = [i for i, x in enumerate(instrument_bool) if x]
        if tab_i != []:
            tab_instrument.append(min(tab_i))
        else:
            tab_instrument.append(None)

    data['instrument'] = tab_instrument
    data['instrument'] = data['instrument'].astype('Int64')
    data['style'] = tab_style
    data['style'] = data['style'].astype('Int64')

    nodes = data[['index', 'user_name', 'poids', 'style', 'instrument']]
    nodes = nodes.rename(columns={'index': 'Id'})
    nodes = nodes.rename(columns={'user_name': 'Label'})

    edges = pd.DataFrame(columns = ['Source', 'Target', 'Type'])
    for i, collab in enumerate(convert_to_adjacency(data)):
        if collab != []:
            for c in collab:
                series = pd.Series([i, c, 'undirected'], index = edges.columns)
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



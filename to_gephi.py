import pandas as pd


def convert_to_adjacency(data):
    """
    Creates list of adjacency for every profile in a given file
    """
    adj_list = []
    for i in range(len(data)):
        user_collabs = str(data.music_collabs[i]).split("\n")
        user_collabs.pop()
        username_collabs = [u.split(" ")[0] for u in user_collabs]
        cand_list = [int(data[data['user_name'] == u].index.values) for u in username_collabs]
        adj_list.append(cand_list)
    return adj_list


def gephi(file):
    """
    Creates nodes and edges files with adjacency list for gephi
    """
    data = pd.read_csv(file)
    data.reset_index(level=0, inplace=True)

    tab_style = []
    tab_instrument = []

    for i in range(len(data)):
        hashtags_cat = str(data.hashtags[i]).split('\n')
        hashtags_cat.pop()
        hashtags_cat_words = [cat.split(': ')[1] for cat in hashtags_cat]
        instr_all = hashtags_cat_words[0].split(', ')
        if instr_all != ['']:
            instr = [i.split(' (')[0] for i in instr_all]
            instr_count = [int(i.split(' (')[1].replace(')', '')) for i in instr_all]
        else:
            instr = ['None']
            instr_count = [0]
        sty_all = hashtags_cat_words[1].split(', ')
        if sty_all != ['']:
            sty = [s.split(' (')[0] for s in sty_all]
            sty_count = [int(s.split(' (')[1].replace(')', '')) for s in sty_all]
        else:
            sty = ['None']
            sty_count = [0]

        # get most used instrument and style
        final_s = sty[sty_count.index(max(sty_count))]
        if final_s:
            tab_style.append(str(final_s))
        else:
            tab_style.append('None')
        final_i = instr[instr_count.index(max(instr_count))]
        if final_i:
            tab_instrument.append(str(final_i))
        else:
            tab_instrument.append('None')

    # add new style and instrument columns
    data['instrument'] = tab_instrument
    data['style'] = tab_style

    # create nodes dataframe
    nodes = data[['index', 'user_name', 'style', 'instrument']]
    nodes = nodes.rename(columns={'index': 'Id'})
    nodes = nodes.rename(columns={'user_name': 'Label'})

    # create edges dataframe
    edges = pd.DataFrame(columns=['Source', 'Target', 'Type'])
    for i, collab in enumerate(convert_to_adjacency(data)):
        if collab != []:
            for c in collab:
                series = pd.Series([i, c, 'undirected'], index=edges.columns)
                edges = edges.append(series, ignore_index=True)

    return nodes, edges


if __name__ == '__main__':

    file_name = str(input("nom fichier : "))
    output = gephi(file_name)
    file_name = file_name.split('.')[0] + '_gephi'
    file_name_nodes = file_name + '_nodes.csv'
    file_name_edges = file_name + '_edges.csv'

    output[0].to_csv(file_name_nodes, index=False)
    output[1].to_csv(file_name_edges, index=False)

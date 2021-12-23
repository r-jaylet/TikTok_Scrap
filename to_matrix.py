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


def convert_to_matrix(graph):
    matrix = []
    for i in range(len(graph)):
        matrix.append([0]*len(graph))
        for j in graph[i]:
            matrix[i][j] = 1
    return matrix


def gephi_matrix(file_name):
    data = pd.read_csv(file_name)
    data.reset_index(level=0, inplace=True)
    data_graph = convert_to_matrix(convert_to_adjacency(data))
    data_graph = pd.DataFrame(data_graph)
    data_graph.reset_index(level=0, inplace=True)
    return data_graph


if __name__ == '__main__':

    file_name = str(input("nom fichier:"))
    output = gephi_matrix(file_name)
    file_name_graph = file_name.split('.')[0] + '_matrix.csv'
    output.to_csv(file_name_graph, index=False)


import networkx as nx
import pandas as pd

def build_graph(data, similarity_matrix, threshold=0.2):
    graph = nx.Graph()
    
    for i, anime in data.iterrows():
        graph.add_node(i, name=anime['name_english'])

    for i in range(len(similarity_matrix)):
        for j in range(i+1, len(similarity_matrix)):
            if similarity_matrix[i, j] > threshold:
                graph.add_edge(i, j, weight=similarity_matrix[i, j])

    return graph

def get_recommendations(graph, anime_title, data, indices, top_n=10):
    if anime_title not in indices:
        return f"'{anime_title}' not found in the dataset."

    idx = indices[anime_title]
    neighbors = list(graph.neighbors(idx))
    
    if not neighbors:
        return []

    similarity_scores = [(i, graph.edges[idx, i]['weight']) for i in neighbors]
    sorted_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    
    if len(sorted_scores) < top_n:
        additional_neighbors = sorted_scores + [(i, graph.edges[idx, i]['weight']) for i in range(len(graph.nodes)) if i not in neighbors][:top_n - len(sorted_scores)]
        sorted_scores = sorted(additional_neighbors, key=lambda x: x[1], reverse=True)
    
    top_scores = sorted_scores[:top_n]
    
    recommended_anime = []
    for i, _ in top_scores:
        anime_name = data.loc[i, 'name_english']
        if anime_name != anime_title:
            recommended_anime.append(anime_name)
    
    return recommended_anime[:top_n]
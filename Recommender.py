import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict
import pymysql
import os
import sys
import tempfile

class Recommender:

    def __init__(self):
        self.database = ""
        self.db = ""
        self.cursor = ""
        self.temp = tempfile.TemporaryFile()
        self.G = nx.Graph()
        self.degree_centrality = ""
        self.players_node = ""
        self.games_node = ""

    def connect(self, db_host, db_user, db_password, db_database):
        self.database = db_database
        self.db = pymysql.connect(host=db_host,user=db_user,password=db_password,database=self.database)
        self.cursor = self.db.cursor()    

    def query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def disconnect(self):
        self.db.close()

    def data_to_txt(self, data, alias):
        container = ""
        for p in data:
            relation = (str(alias) + str(p[1])) if p[1]!=None else "" 
            container += str(p[0]) + " " + relation + "\n"

        return container

    def set_graph(self, dataset):
        try:           
            self.temp.write(dataset.encode("utf-8"))
            self.temp.seek(0)

            self.G=nx.read_adjlist(self.temp)
        finally:
            self.temp.close()

    def create_partitions(self):
        for nodes in self.G.nodes():
            if(nodes[:1]=='g'):
                self.G.nodes[nodes]['bipartite'] = 'games'
            else:
                self.G.nodes[nodes]['bipartite'] = 'players'
        self.G.nodes(data=True) 

    def get_nodes_from_partition(self, partition):
        nodes = []

        for n in self.G.nodes():
            if self.G.nodes[n]['bipartite'] == partition:
                nodes.append(n)

        return nodes

    def compute_degree_centrality(self):
        self.degree_centrality = nx.degree_centrality(self.G)

    def set_nodes_from_partition(self, node):
        if (node=="players"):
            self.players_node = self.get_nodes_from_partition(node) 
            return self.players_node    
        if (node=="games"):
            self.games_node = self.get_nodes_from_partition(node)
            return self.games_node

    def get_degree_centrality(self, node):
        if (node=="players"):
            return [self.degree_centrality[n] for n in self.players_node]    
        if (node=="games"):
            return [self.degree_centrality[n] for n in self.games_node]       

    def get_shared_partitions_between_nodes(self, node1, node2):
        assert self.G.nodes[node1]['bipartite'] == self.G.nodes[node2]['bipartite']

        neighbors_1 = self.G.neighbors(node1)
        neighbors_2 = self.G.neighbors(node2)

        self.G.edges(data=True)

        # Compute the overlap
        return set(neighbors_1).intersection(neighbors_2)

    def players_similarities(self, player1, player2):
        # Check that the nodes belong to the 'players' partition
        assert self.G.nodes[player1]['bipartite'] == 'players'
        assert self.G.nodes[player2]['bipartite'] == 'players'

        # Get the set of nodes shared between the two users
        shared_nodes = self.get_shared_partitions_between_nodes(player1, player2)

        # Return the fraction of nodes in the games partition
        return len(shared_nodes) / len(self.games_node)

    def most_similar_players(self, player_id):
        assert self.G.nodes[player_id]['bipartite'] == 'players'

        players_node = set(self.players_node)
        players_node.remove(player_id)

        # Create the dictionary: similarities
        similarities = defaultdict(list)
        for n in players_node:
            similarity = self.players_similarities(player_id, n)
            similarities[similarity].append(n)

        max_similarity = max(similarities.keys())

        return similarities[max_similarity]

    def recommended_games(self, from_user, to_user):
        from_games = set(self.G.neighbors(from_user))
        to_games = set(self.G.neighbors(to_user))

        return list(from_games.difference(to_games))

    def get_recommended_games_names(self, query):
        return self.query(query)

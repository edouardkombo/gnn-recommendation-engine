from . import Recommender
import json
from flask import Flask,jsonify,request,render_template, Response

app = Flask(__name__)

@app.route('/')
def default():
    engine = Recommender()

    engine.connect(db_host="", db_user="", db_password="", db_database="")

    # Get query results
    
    # Players should have the prefix "p" before
    # Games should have the prefix "g" before
    players = engine.query("") # All the games related to a single player (YOU MUST RETURN ONLY THE IDs)
    games = engine.query("") # All the players related to a single game (YOU MUST RETURN ONLY THE IDs)

    # Transform data and get dataset
    players_data = engine.data_to_txt(players, "g") # g represent games
    games_data = engine.data_to_txt(games, "p") # p represent players
    dataset = players_data + "\\n" + games_data

    # Create the Graph network and the partitions
    engine.set_graph(dataset)
    engine.create_partitions()

    # Set each nodes
    engine.set_nodes_from_partition('players')
    engine.set_nodes_from_partition('games')

    # Compute the degree centralities
    engine.compute_degree_centrality()

    # Get the degree centralities for players and games nodes
    players_degree_centrality = engine.get_degree_centrality("players")
    games_degree_centrality = engine.get_degree_centrality("games")


    user_id = request.args.get('user_id') if request.args.get('user_id') else "1"
    from_player_id = "p" + user_id
    print("USER_ID ", user_id)

    #print(len(engine.get_shared_partitions_between_nodes(from_player_id, to_player_id)))

    # Compute the similarity score between users 'u4560' and 'u1880'
    #similarity_score = engine.players_similarities(from_player_id, to_player_id)
    #print("Similarity score ", similarity_score)

    # Get most recommended players and the best one
    msp = engine.most_similar_players(from_player_id)
    to_player_id = msp[0]
    to_player_id_clean = msp[0].replace('p','')
    look_alike_player = engine.query("") # Search for the player id with to_player_id_clean
    print("Most similar players ", msp)
    print("look alike player ", look_alike_player)


    # Get recommended games as a list
    recommended_games = engine.recommended_games(from_player_id, to_player_id)
    print("Recommended games ", recommended_games)


    # Get recommended games in real format
    where_games = (",".join(recommended_games)).replace("g","")
    if len(where_games)==0:
        real_recommendations = []
    else:    
        real_recommendations = engine.query("")  # Query for the list of games within a list (SELECT * FROM xxx WHERE id IN(...) )
    print("Real game recommendations ", json.dumps(real_recommendations,indent=4))

    engine.disconnect()    
    return jsonify(json.dumps(real_recommendations))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, port=4000)    








# Recommendation engine using GNN (Graph Neural Network) and bipartite

The goal of this project is to recommend to some players, potential games they would be likely to play based upon other players interactions, so the system will learn by itself.

For this project I am using mysql and my database has four tables:
- Players
- Games
- Players_games_sessions (interactions between players and games)

Gunicorn is used as a server, FLask as light framework and networkx to compute the graph.

## Understanding of Bipartite GNN

![](bipartite.gif)

### Sufficient Condition
Let G=(V,E) be bipartite.

So, let V=A∪B such that A∩B=∅ and that all edges e∈E are such that e is of the form {a,b} where a∈A and b∈B.

(This is the definition of a bipartite graph.)


#### Suppose G has (at least) one odd cycle C.

Let the length of C be n.

Let C=(v1,v2,…,vn,v1).

Without loss of generality, let v1∈A. It follows that v2∈B and hence v3∈A, and so on.

Hence we see that ∀k∈{1,2,…,n}, we have:

vk∈{A:B:k oddk even
But as n is odd, vn∈A.

But v1∈A, and vnv1∈Cn.

So vnv1∈E which contradicts the assumption that G is bipartite.

Hence if G is bipartite, it has no odd cycles.



### Necessary Condition
It is enough to consider G as being connected, as otherwise we could consider each component separately.


#### Suppose G has no odd cycles.

Choose any vertex v∈G.

Divide G into two sets of vertices like this:

Let A be the set of vertices such that the shortest path from each element of A to v is of odd length
Let B be the set of vertices such that the shortest path from each element of B to v is of even length.
Then v∈B and A∩B=∅.


#### Suppose a1,a2∈A are adjacent.

Then there would be a closed walk of odd length (v,…,a1,a2,…,v).

But from Graph containing Closed Walk of Odd Length also contains Odd Cycle, it follows that G would then contain an odd cycle.

This contradicts our initial supposition that G contains no odd cycles.

So no two vertices in A can be adjacent.


By the same argument, neither can any two vertices in B be adjacent.


Thus A and B satisfy the conditions for G=(A∪B,E) to be bipartite.
(Source wikipedia)


## Installation

Clone the repository, and install the required dependencies

```bash
pip install -r requirements.txt
```

Open app.py, and:

1. define the credentials to your database

```bash
engine.connect(db_host="", db_user="", db_password="", db_database="")
```

2. Specify the queries

```bash
# Get query results

# Players should have the prefix "p" before
# Games should have the prefix "g" before
players = engine.query("") # All the games related to a single player (YOU MUST RETURN ONLY THE IDs)
games = engine.query("") # All the players related to a single game (YOU MUST RETURN ONLY THE IDs)
```

Query sample
```mysql
SELECT CONCAT('p', pgs.player_id) as player_id, GROUP_CONCAT(ga.id SEPARATOR ' g') as game_ids 
FROM players_game_sessions pgs 
LEFT JOIN games ga ON ga.game_id = pgs.game_id 
GROUP BY pgs.player_id;
```

Internally, the engine will compute your query results in a txt graph format like this one:
```
p123 g345 g84595 g41528 # Games played by one player
g123 p45454 p66455354 p5335535 p245655 p3535353 # All players linked to a game
p456 # This player had played no game yet
```

3. Specify the query to retrieve data of the most similar player

```bash
look_alike_player = engine.query("") # Search for the player id with to_player_id_clean
```

4. Specify the query to retrieve complete details of each recommended game

```bash
real_recommendations = engine.query("") # Query for the list of games within a list (SELECT * FROM xxx WHERE id IN(...) )
```

## Usage

Run the server

```python
gunicorn app:app
```

Enter a player id from your url bar

```
http://127.0.0.1:3000?user_id=xxxxxxx
```

Get the recommendations as json format

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)

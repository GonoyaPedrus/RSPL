import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Exemple de données (à remplacer par vos propres données)
data = pd.read_csv('/Users/melusinecaillard/RSPL/data/2023-24/cleaned_players.csv')

df = pd.DataFrame(data)

# Combinez certaines caractéristiques en une seule chaîne de texte
df['Caracteristiques'] = df['Position'] + ' ' + df['Buts'].astype(str) + 'b ' + df['Passes'].astype(str) + 'p ' + df['CartonsJaunes'].astype(str) + 'cj'

# Utilisez TF-IDF pour créer une matrice de caractéristiques
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(df['Caracteristiques'])

# Calcul de la similarité cosinus entre les joueurs
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# Fonction pour obtenir des recommandations
def get_recommendations(player, cosine_similarities, df):
    player_index = df[df['Joueur'] == player].index[0]
    similar_players = list(enumerate(cosine_similarities[player_index]))
    similar_players = sorted(similar_players, key=lambda x: x[1], reverse=True)
    similar_players = similar_players[1:4]  # Exclude the player itself
    similar_player_indices = [x[0] for x in similar_players]
    return df['Joueur'].iloc[similar_player_indices]

# Exemple d'utilisation
user_choice = 'Messi'
recommendations = get_recommendations(user_choice, cosine_sim, df)
print(f"Recommandations pour {user_choice}: {', '.join(recommendations)}")

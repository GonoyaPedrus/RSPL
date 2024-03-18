import pandas as pd
import boto3
import json
import os

# Charger les informations d'identification à partir du fichier de configuration
with open('src/config.json') as f:
    config = json.load(f)

aws_access_key_id = config['AWS_ACCESS_KEY_ID']
aws_secret_access_key = config['AWS_SECRET_ACCESS_KEY']

# Créer une connexion S3 en utilisant les variables d'environnement
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Nom du bucket S3
bucket_name = 'myfplbucket1'

# Préfixe du dossier dans S3 où se trouvent les fichiers gw
dossier_prefix = 'data/2023-24/players/'

for nom_joueur in os.listdir(dossier_prefix):
    # Chemin complet du dossier du joueur dans S3
    chemin_s3_joueur = dossier_prefix + nom_joueur + '/'
    # Chemin de destination local du joueur
    chemin_destination_joueur = 'data/2023-24/players/' + nom_joueur + '/'
    # Créer le dossier de destination s'il n'existe pas
    if not os.path.exists(chemin_destination_joueur):
        os.makedirs(chemin_destination_joueur)

    # Obtenir la liste des objets dans le dossier du joueur
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=chemin_s3_joueur)

    # Vérifier si des objets correspondants ont été trouvés
    if 'Contents' in response:
        # Boucle à travers chaque objet trouvé
        for obj in response['Contents']:
            key = obj['Key']
            # Télécharger le fichier si son nom est gw.csv
            if os.path.basename(key) == 'gw.csv':
                # Télécharger le fichier dans le répertoire local du joueur
                nom_fichier_local = chemin_destination_joueur + 'gw.csv'
                s3.download_file(bucket_name, key, nom_fichier_local)
                print(f"Le fichier {key} a été téléchargé avec succès pour le joueur {nom_joueur}.")
    else:
        print(f"Aucun fichier trouvé pour le joueur {nom_joueur}.")

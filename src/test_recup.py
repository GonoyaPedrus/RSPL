import pandas as pd
import boto3
import json

# Charger les informations d'identification à partir du fichier de configuration
with open('config.json') as f:
    config = json.load(f)

aws_access_key_id = config['AWS_ACCESS_KEY_ID']
aws_secret_access_key = config['AWS_SECRET_ACCESS_KEY']


#Créer une connexion S3 en utilisant les variables d'environnement
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Nom du bucket S3
bucket_name = 'myfplbucket1'

# Préfixe du dossier dans S3 où se trouvent les fichiers gw
dossier_prefix = 'data/2023-24/gws/'

# Rechercher le fichier gw le plus récent
fichier_gw_recent = None
dernier_num_gw = 0

for num_gw in range(1, 39):
    nom_fichier_s3 = f'{dossier_prefix}gw{num_gw}.csv'
    try:
        s3.head_object(Bucket=bucket_name, Key=nom_fichier_s3)
        dernier_num_gw = num_gw
    except Exception as e:
        # Le fichier n'existe pas, passer au suivant
        pass

# Si aucun fichier gw n'a été trouvé, sortir
if dernier_num_gw == 0:
    print("Aucun fichier gw trouvé dans le dossier.")
    exit()

# Télécharger le fichier gw le plus récent
nom_fichier_s3_recent = f'{dossier_prefix}gw{dernier_num_gw}.csv'
chemin_local_recent = f'../data/2023-24/gws/gw{dernier_num_gw}.csv'
s3.download_file(bucket_name, nom_fichier_s3_recent, chemin_local_recent)

# Lire le fichier CSV avec pandas
df = pd.read_csv(chemin_local_recent)

# Afficher les premières lignes du DataFrame pour vérifier si le fichier a été correctement lu
print(df.head())
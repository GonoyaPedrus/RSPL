import os
import boto3
from dotenv import load_dotenv

# Charger les variables d'environnement à partir de .env
load_dotenv()

# Utiliser les variables d'environnement
aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Initialisez le client S3
s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

# Remplacez 'myfplbucket1' par le nom de votre bucket S3
bucket_name = 'myfplbucket1'

# Liste les objets dans le bucket
try:
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix='data/2023-24')  # Spécifiez le chemin de votre dossier
    # Si vous ne spécifiez pas de préfixe, tous les objets du bucket seront listés.

    # Vérifiez si des objets sont disponibles dans le bucket
    if 'Contents' in response:
        print("Objets dans le dossier:")
        for obj in response['Contents']:
            print(obj['Key'])  # Affiche le nom de l'objet
    else:
        print("Le dossier est vide.")

except Exception as e:
    print("Une erreur s'est produite:", e)

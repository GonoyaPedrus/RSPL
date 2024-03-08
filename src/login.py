import pymysql

# Connexion à la base de données
db = pymysql.connect(
    host='database-1.clq2ucwoa2c5.us-east-1.rds.amazonaws.com',
    port=3306,
    user='admin',
    passwd='12345678',
)

# Création d'un objet curseur
cursor = db.cursor()

# Suppression de la base de données si elle existe déjà
sql = "DROP DATABASE IF EXISTS loginperson"
cursor.execute(sql)

# Création de la base de données loginperson
sql = "CREATE DATABASE loginperson"
cursor.execute(sql)

# Sélection de la base de données loginperson
sql = "USE loginperson"
cursor.execute(sql)

# Création de la table person
sql = """
CREATE TABLE person (
    id INT NOT NULL AUTO_INCREMENT,
    username TEXT,
    password TEXT,
    PRIMARY KEY (id)
)"""
cursor.execute(sql)

# Affichage des tables pour vérification
sql = "SHOW TABLES"
cursor.execute(sql)
print(cursor.fetchall())

# Insertion de données dans la table person
sql = "INSERT INTO person(username, password) VALUES (%s, %s)"
cursor.execute(sql, ('victor', 'azerty'))

# Valider la transaction
db.commit()
sql = """select * from person"""
cursor.execute(sql)
print(cursor.fetchall())
# Fermeture de la connexion
db.close()

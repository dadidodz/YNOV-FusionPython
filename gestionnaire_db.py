import sqlite3

connection = sqlite3.connect("fusion.sqlite")

print(connection.total_changes)

cursor = connection.cursor()

cursor.execute("CREATE TABLE HistoriqueMessage(Id_Message COUNTER,Id_Joueur INT,Id_Partie INT, Contenu VARCHAR(50),  DateHeureEnvoi DATETIME,   PRIMARY KEY(Id_Message))")

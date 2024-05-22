import sqlite3
connection = sqlite3.connect("fusion.sqlite")
cursor = connection.cursor()

if (data):
        cursor.execute(f"INSERT INTO HistoriqueMessage(Id_Joueur, Id_Partie, Contenu, DateHeureEnvoi) VALUES (1, 1, '{data.decode()}', '2024-04-11 17:29:30')")
        # cursor.execute(f"INSERT INTO HistoriqueMessage(Contenu) VALUES ('{data.decode()}')")
        # print(cursor.execute(f"INSERT INTO HistoriqueMessage(Contenu) VALUES ('{data.decode()}')"))
        connection.commit()
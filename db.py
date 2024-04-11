import sqlite3

connection = sqlite3.connect("fusion.sqlite")

print(connection.total_changes)

cursor = connection.cursor()

cursor.execute("CREATE TABLE HistoriqueMessage(Id_Message COUNTER,Id_Joueur INT,Id_Partie INT, Contenu VARCHAR(50),  DateHeureEnvoi DATETIME,   PRIMARY KEY(Id_Message))")
cursor.execute("CREATE TABLE Partie(   Id_Partie COUNTER,   Durée VARCHAR(50),   PRIMARY KEY(Id_Partie))")
cursor.execute("CREATE TABLE HistoriquePartie(   Id_Partie INT,   Durée INT,   Gagnant VARCHAR(50),   Id_Joueur1 INT,   Id_Joueur2 INT,   PRIMARY KEY(Id_Partie))")
cursor.execute("CREATE TABLE Joueur(Id_Joueur COUNTER, Pseudo VARCHAR(50) NOT NULL, IP VARCHAR(50), MMR INT,   Mot_de_passe VARCHAR(50),   EnAttente LOGICAL,   Id_Partie INT,   PRIMARY KEY(Id_Joueur),   UNIQUE(Pseudo),   FOREIGN KEY(Id_Partie) REFERENCES Partie(Id_Partie))")

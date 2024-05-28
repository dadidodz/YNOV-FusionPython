import time
from chat import Chat
import sqlite3

class MorpionServeur:
    """
    Classe MorpionServeur

    Attributs : 
        id_partie (str) : Stock l'id de la partie
        time_last_action (float) : Stock le timestamp de la dernière action de la partie
        chat (Chat) : Objet Chat de la partie
        pseudo_P1 (str) : Stocke le pseudo du joueur 1
        pseudo_P2 (str) : Stocke le pseudo du joueur 2
        players (dict) : Dictionnaire pour assigner un pseudo à un signe
        current_player (str): Pseudo du joueur qui doit jouer
        actions_history (list): Historique des actions de la partie
        board (list): Liste à deux dimensions utilisée comme plateau de jeu
        is_game_finished (bool): Booléen de l'état de la partie
        winner (str) : Pseudo du gagnant
        loser (str) : Pseudo du perdant
    """
    def __init__(self, id_partie, pseudo_P1, pseudo_P2):
        """
        Initialise les attributs de MorpionServeur.
        """
        self.id_partie = id_partie
        self.time_last_action = time.time()
        self.chat = Chat()
        self.pseudo_P1 = pseudo_P1
        self.pseudo_P2 = pseudo_P2
        self.players = {}
        self.players[self.pseudo_P1] = "X"
        self.players[self.pseudo_P2] = "O"
        self.current_player = pseudo_P1
        self.actions_history = []
        self._board = [[" " for _ in range(3)] for _ in range(3)]
        self.is_game_finished = False
        self.winner = None
        self.loser = None

    def play(self, row, col, pseudo_player):
        """
        Ajoute le coup joué au plateau de jeu.
        """
        if not self.is_game_finished: # Si la partie n'est pas finie
            connection = sqlite3.connect("fusion.sqlite")
            cursor = connection.cursor()
            if self.current_player == pseudo_player: # Si le pseudo de la personne qui joue est bien celui de celui qui doit jouer
                if self.board[row][col] == " ": # Si la case est vide
                    self.board[row][col] = self.players[self.current_player] # Ajoute le signe du joueur dans la plateau de jeu
                    sql = '''
                    INSERT INTO Parties (Id_Partie, Ligne, Colonne, Pseudo)
                    VALUES (?, ?, ?, ?)
                    '''
                    data = (self.id_partie, row, col, self.current_player)
                    cursor.execute(sql, data) # Stocke l'action dans la base de données
                    
                    self.time_last_action = time.time() # Met à jour le timestamp de la dernière action

                    if self.check_winner(): # Si, à la suite du coup joué, il y a un gagnant
                        self.is_game_finished = True 
                        self.winner = self.current_player
                        if self.current_player == self.pseudo_P1:
                            self.loser = self.pseudo_P2
                        else:
                            self.loser = self.pseudo_P1
                        
                        # Ajoute l'action à l'historique des actions
                        self.actions_history.append((row, col, self.players[self.current_player], self.is_game_finished, self.winner, self.loser , self.current_player, time.time()))
                        sql = '''
                        DELETE FROM Parties
                        WHERE Id_Partie = ?
                        '''
                        data = (self.id_partie,)
                        cursor.execute(sql, data) # Supprime de la base de données les coups joués dans la partie
                        
                        sql = '''
                        INSERT INTO HistoriqueParties (Id_Partie, Gagnant, Perdant, Pseudo_J1, Pseudo_J2)
                        VALUES (?, ?, ?, ?, ?)
                        '''
                        data = (self.id_partie, self.winner, self.loser, self.pseudo_P1, self.pseudo_P2)
                        cursor.execute(sql, data) # Ajoute le résultat de la partie dans la base de données

                    elif self.is_board_full(): #  Si, à la suite du coup joué, le plateau de jeu est plein
                        self.is_game_finished = True
                        self.actions_history.append((row, col, self.players[self.current_player], self.is_game_finished, self.winner, self.loser , self.current_player, time.time()))
                        sql = '''
                        DELETE FROM Parties
                        WHERE Id_Partie = ?
                        '''
                        data = (self.id_partie,)
                        cursor.execute(sql, data)
                        
                        sql = '''
                        INSERT INTO HistoriqueParties (Id_Partie, Gagnant, Perdant, Pseudo_J1, Pseudo_J2)
                        VALUES (?, ?, ?, ?, ?)
                        '''
                        data = (self.id_partie, self.winner, self.loser, self.pseudo_P1, self.pseudo_P2)
                        cursor.execute(sql, data)

                    else:
                        self.actions_history.append((row, col, self.players[self.current_player], self.is_game_finished, None, None, self.current_player,time.time()))
                        self.current_player = self.pseudo_P2 if self.current_player == self.pseudo_P1 else self.pseudo_P1 # Modifie le joueur qui doit jouer
                    connection.commit()
            connection.close()
                        
    def get_actions_after_time(self, timestamp):
        """
        Récupère les actions qui ont été jouées depuis le timestamp en paramètre.

        Paramètre:
        timestamp (float) : timestamp de la dernière fois où le client a récupéré les actions

        Retour :
        action_after_time (list) : Liste de toutes les actions depuis la dernière fois
        """
        action_after_time = [(row, col, txt, etat_partie, winner, loser, current_player ) for row, col, txt, etat_partie, winner, loser, current_player, action_time in self.actions_history if action_time > timestamp]
        return action_after_time
    
    @property
    def board(self):
        """
        Getter de self._board
        """
        return self._board

    def check_winner(self):
        """
        Vérifie si un des deux joueurs a gagné en alignant 3 de ses symboles.
        """
        for i in range(3):
            if self.board[i][0] == self.board[i][1] == self.board[i][2] != " ":
                return True
            if self.board[0][i] == self.board[1][i] == self.board[2][i] != " ":
                return True
        if self.board[0][0] == self.board[1][1] == self.board[2][2] != " ":
            return True
        if self.board[0][2] == self.board[1][1] == self.board[2][0] != " ":
            return True
        return False

    def is_board_full(self):
        """
        Vérifie si le plateau de jeu est plein.
        """
        for row in self.board:
            if " " in row:
                return False
        return True
import tkinter as tk
from tkinter import messagebox
import time
from chat import Chat

class MorpionServeur:
    # def __init__(self, id_partie, addr_joueur1, addr_joueur2, pseudo_j1, pseudo_j2):
    def __init__(self, id_partie, pseudo_j1, pseudo_j2):
        self.id_partie = id_partie
        self.temps_derniere_action = time.time()
        self.chat = Chat()
        self.pseudo_j1 = pseudo_j1
        self.pseudo_j2 = pseudo_j2
        self.joueurs = {}
        self.joueurs[self.pseudo_j1] = "X"
        self.joueurs[self.pseudo_j2] = "O"
        self.current_player = pseudo_j1
        self.historique_actions = []
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        self.is_partie_finie = False
        self.gagnant = None
        self.perdant = None

    def jouer(self, row, col, pseudo_joueur):
        if not self.is_partie_finie:
            if self.current_player == pseudo_joueur:
                if self.board[row][col] == " ":
                    self.board[row][col] = self.joueurs[self.current_player]
                    
                    self.temps_derniere_action = time.time()

                    if self.check_winner():
                        self.is_partie_finie = True
                        self.gagnant = self.current_player
                        if self.current_player == self.pseudo_j1:
                            self.perdant = self.pseudo_j2
                        else:
                            self.perdant = self.pseudo_j1

                        self.historique_actions.append((row, col, self.joueurs[self.current_player], self.is_partie_finie, self.gagnant, self.current_player, self.perdant ,time.time()))
                    elif self.is_board_full():
                        self.is_partie_finie = True
                        self.historique_actions.append((row, col, self.joueurs[self.current_player], self.is_partie_finie, self.gagnant, self.current_player, self.perdant ,time.time()))
                    else:
                        self.historique_actions.append((row, col, self.joueurs[self.current_player], self.is_partie_finie, None, None, self.current_player,time.time()))
                        self.current_player = self.pseudo_j2 if self.current_player == self.pseudo_j1 else self.pseudo_j1
                        
    def get_actions_after_time(self, timestamp): # le serveur demande au morpion si après chaque seconde il y'a un nouveau coup
        # Récupérer les messages envoyés après le temps donné
        action_after_time = [(row, col, txt, etat_partie, gagnant, perdant, current_player ) for row, col, txt, etat_partie, gagnant, perdant,current_player, action_time in self.historique_actions if action_time > timestamp]
        return action_after_time

    def check_winner(self):
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
        for row in self.board:
            if " " in row:
                return False
        return True
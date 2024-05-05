import tkinter as tk
from tkinter import messagebox
import time

class MorpionServeur:
    def __init__(self, id_partie, addr_joueur1, addr_joueur2):
        self.id_partie = id_partie
        self.temps_derniere_action = time.time()
        self.joueurs = {}
        self.joueurs[addr_joueur1] = "X"
        self.joueurs[addr_joueur2] = "O"
        self.current_player = addr_joueur1
        self.historique_actions = []
        self.board = [[" " for _ in range(3)] for _ in range(3)]

    def jouer(self, row, col, addr_joueur):
        if self.current_player == addr_joueur:
            if self.board[row][col] == " ":
                self.board[row][col] = self.joueurs[self.current_player]
                self.historique_actions.append((row, col, self.joueurs[self.current_player], time.time()))
                self.temps_derniere_action = time.time()

                # if self.check_winner():
                #     gagnant
                #     messagebox.showinfo("Fin de partie", f"Le joueur {self.current_player} a gagné!")
                #     self.reset_game()
                # elif self.is_board_full():
                #     messagebox.showinfo("Fin de partie", "Match nul!")
                #     self.reset_game()
                # else:
                #     self.current_player = self.joueurs[addr_joueur2] if self.current_player == self.joueurs[addr_joueur1] else self.joueurs[addr_joueur1]
    
    def get_actions_after_time(self, timestamp):
        # Récupérer les messages envoyés après le temps donné
        action_after_time = [(row, col, txt) for row, col, txt, action_time in self.historique_actions if action_time > timestamp]
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

    def reset_game(self):
        self.board = [[" " for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                self.buttons[i][j].config(text="")
        self.current_player = "X"

    def run(self):
        self.window.mainloop()

# Utilisation du jeu de Morpion
if __name__ == "__main__":
    morpion = Morpion()
    morpion.run()

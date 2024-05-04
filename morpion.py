import tkinter as tk
from tkinter import messagebox

class Morpion:
    def __init__(self, id_partie, joueur1, joueur2):
        self.window = tk.Tk()
        self.window.title("Morpion")

        self.id_partie = id_partie

        self.current_player = "X"
        self.board = [[" " for _ in range(3)] for _ in range(3)]

        self.buttons = [[None for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                button = tk.Button(self.window, text="", font=("Helvetica", 24), width=4, height=2,
                                   command=lambda row=i, col=j: self.play(row, col))
                button.grid(row=i, column=j)
                self.buttons[i][j] = button

    def play(self, row, col):
        if self.board[row][col] == " ":
            self.board[row][col] = self.current_player
            self.buttons[row][col].config(text=self.current_player)
            
            if self.check_winner():
                messagebox.showinfo("Fin de partie", f"Le joueur {self.current_player} a gagné!")
                self.reset_game()
            elif self.is_board_full():
                messagebox.showinfo("Fin de partie", "Match nul!")
                self.reset_game()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"

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

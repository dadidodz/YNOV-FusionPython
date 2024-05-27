import tkinter as tk
from tkinter import ttk

# Création de la fenêtre principale
root = tk.Tk()
root.title("Entrée de mot de passe")

# Création d'une étiquette pour le champ de mot de passe
password_label = ttk.Label(root, text="Mot de passe:")
password_label.pack(pady=10)

# Création de l'entrée de mot de passe avec l'option 'show' pour masquer le texte
password_entry = ttk.Entry(root, show="*")
password_entry.pack(pady=10)

# Fonction pour obtenir le mot de passe saisi
def get_password():
    print("Mot de passe saisi:", password_entry.get())

# Bouton pour valider le mot de passe
submit_button = ttk.Button(root, text="Soumettre", command=get_password)
submit_button.pack(pady=10)

# Boucle principale de l'application
root.mainloop()

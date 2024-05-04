import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# Création d'un style ttk pour les boutons
style = ttk.Style()

# Configuration du style pour le bouton
style.configure("Custom.TButton",
                height=50,  # Définit la hauteur du bouton
                )

# Création du bouton ttk avec le style personnalisé
bouton_ttk = ttk.Button(root, text="", style="Custom.TButton")
bouton_ttk.pack()

root.mainloop()

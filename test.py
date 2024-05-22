import tkinter as tk
from tkinter import ttk

def ajouter_texte_gris_italique():
    txt = "Votre texte en gris et italique\n"
    end_index_before_insert = chat_display.index(tk.END)
    chat_display.insert(tk.END, txt)
    end_index_after_insert = chat_display.index(tk.END)
    chat_display.tag_add('gris_italique', end_index_before_insert, end_index_after_insert)

def ajouter_texte_defaut():
    txt = "Votre texte par défaut\n"
    chat_display.insert(tk.END, txt)

root = tk.Tk()

# Créer un widget Text de Tkinter
chat_display = tk.Text(root)
chat_display.pack()

# Définir le tag pour le texte gris et italique
chat_display.tag_configure('gris_italique', foreground='grey', font=('Helvetica', 12, 'italic'))

# Utiliser ttk pour les boutons
ajouter_texte_italique_button = ttk.Button(root, text="Ajouter Texte Italique", command=ajouter_texte_gris_italique)
ajouter_texte_italique_button.pack()

ajouter_texte_defaut_button = ttk.Button(root, text="Ajouter Texte Défault", command=ajouter_texte_defaut)
ajouter_texte_defaut_button.pack()

root.mainloop()

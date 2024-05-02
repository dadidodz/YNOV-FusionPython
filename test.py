import tkinter as tk

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat App")

        # Zone de texte pour afficher les messages
        self.chat_display = tk.Text(root, height=20, width=50, state=tk.DISABLED)
        self.chat_display.pack()

        # Zone de saisie pour taper les messages
        self.entry = tk.Entry(root, width=50)
        self.entry.pack()

        # Bouton pour envoyer les messages
        self.send_button = tk.Button(root, text="Envoyer", command=self.send_message)
        self.send_button.pack()

    def send_message(self):
        # Récupérer le message saisi dans l'Entry
        message = self.entry.get()
        if message:
            self.chat_display.configure(state=tk.NORMAL)
            # Afficher le message dans la zone de texte
            self.chat_display.insert(tk.END, f"You: {message}\n")

            self.chat_display.configure(state=tk.DISABLED)
            # Effacer le contenu de l'Entry après l'envoi du message
            self.entry.delete(0, tk.END)

# Créer une fenêtre tkinter
root = tk.Tk()
# Créer une instance de l'application de chat
chat_app = ChatApp(root)
# Lancer la boucle principale de tkinter
root.mainloop()

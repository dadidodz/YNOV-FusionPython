class Joueur:
    def __init__(self, nom, email, mmr, adresse_ip, mot_de_passe, en_attente):
        self.nom = nom
        self.email = email
        self.mmr = mmr
        self.adresse_ip = adresse_ip
        self.mot_de_passe = mot_de_passe
        self.en_attente = en_attente

# Exemple d'utilisation
joueur1 = Joueur("John Doe", "john.doe@example.com", 1500, "192.168.0.1", "password123", True)
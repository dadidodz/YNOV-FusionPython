
# Logiciel morpion en réseau 

c'est un logiciel qui permet de jouer au morpion en ligne (localement).

## En executable

 - [Ouvrez simplement l'éxécutable](https://code.visualstudio.com/)



##  Pré requis (si vous n'avez pas l'éxécutable)

 - [Visual Studio Code](https://code.visualstudio.com/)
 - [Python 3.12](https://www.python.org/downloads/)
 - [pip3](https://www.journaldunet.fr/developpeur/developpement/1441239-comment-installer-pip-3-sur-windows/#:~:text=Pip3%20est%20le%20gestionnaire%20de,issue%20de%20la%20branche%203.)
 
 ## Comment utiliser  le projet ?

### Ouvrez un terminal et clonez le projet :

```http
 git clone https://github.com/dadidodz/YNOV-FusionPython.git
```
### Déplacez vous ensuite dans le projet
```http
 cd YNOV-FusionPython
```

### Python3 & Environnement virtuel :

##### nous allons crée un environnement virtuel python pour installer les librairies pour le bon fonctionnement du projet. **Créez vous donc un environnement virtuel puis lancez le**

 - #### Crée un environnement virtuel python3
```http
  python3 -m venv env
```
- #### Pour lancer l'environnement python3
```http
  source env/bin/activate
```
- #### *pour désactiver l'environnement python3*
```http
   deactivate
```
Note : *[en savoir plus sur les environnements virtuels python](https://openclassrooms.com/fr/courses/6951236-mettez-en-place-votre-environnement-python/7013854-decouvrez-les-environnements-virtuels)*

## Installer les dépendances nécéssaires :

```http
    pip install -r requirements.txt
```

#### Voici à quoi nous sert chaque librairie :


| Librairie      | Description                |
| :--------      |          :--------                      |
| `bcrypt`  ` `  | `Générateur de hash`



## Comment jouer ? 
modifier le fichier config.txt en mettant l'adresse du serveur IPV4 (choissisez un ordinateur qui sera serveur + client)


**attention ne changé pas les ports**
### Lancer 2 terminaux sur votre machine :

| Terminal      | commande                |
| :--------      |          :--------                      |
| `Terminal 1 :  Serveur`  ` `  | `cd Serveur` |
| `Terminal 2 :  Client`  ` `  | `cd Client` |

### Exécutez les 2 commandes :

| Terminal      | commande                |
| :--------      |          :--------                      |
| `Terminal 1 :  Serveur`  ` `  | `python3 serveurUDP.py`
| `Terminal 2 :  Client`  ` `  | `python3 clientUDP.py` |

##### invitez maintenant un ami à jouer, en suivant les instructions uniquement pour du terminal 2


##### (*verifiez que le 2e client à bien l'addresse du serveur dans le fichier config.txt*)


## Support

Pour le support, email  : dorian.blatiere@ynov.com ou nils.jaudon@ynov.com 



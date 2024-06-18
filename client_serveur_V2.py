# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : client serveurs
# Date : 20/06/24

import multiprocessing as mp
import time, random
from queue import Empty

#to do
# M <N et autres empty

# Version 2 : m demandeurs, n calculteurs. (5 points)

""" on a plusieurs demandeurs di , i = 1..m.
Dans ce cas, pour que les demandeurs récupèrent leurs propres résultats, il faudra identifier les
demandes par le demandeur di .
Dans un premier temps, on peut gérer une Queue par demandeur. Lorsque un résultat est cal-
culé et déposé par un processus calculateur, le demandeur peut récupérer ce résultat dans la file
(Queue) qui lui est dédiée.
(3) Réaliser cette version en créant plusieurs demandeurs et plusieurs calculateurs capables de
traiter des demandes de calculs fréquentes.

(4) Comment faire si ne souhaite pas créer une Queue par demandeur ?
Dans ce cas, lorsque un résultat est calculé et déposé par un processus calculateur, il ajoute l’iden-
tifiant di du demandeur. Ainsi, le demandeur peut filtrer la Queue (unique) des résultats pour
trouver les réponses à ses demandes.
 """

# Objectif : process commande qui genere M commandes et dépot dans la queue unique commandes avec un id
# puis se met en attente jusqu'à récupurer son resultat danq la queue reponses en filtrant
# Args:   id (int) du demandeur, queue commandes, queue reponses

def demandeur(id, commandes, reponses):        
    operateur=random.choice(["+", "-", "*", "/"])   # generation de la commande aléatoire
    opd1 = random.randint(1,10)
    opd2 = random.randint(1,10)
    commande = str(opd1) + operateur + str(opd2)

    commandes.put((id, commande))     # ajout de la commande dans la queue demandeur avec son id
    print("Le demandeur", id, "a déposé le calcul", commande)
 
    while True:     # récupere son propre resultat dans la queue reponse en filtrant avec son id
        di, reponse = reponses.get()     
        if di == id :
            print("Le resultat du demandeur", id, "est :", reponse)
            break
        else :
            reponses.put((di, reponse))
            time.sleep(0.01)


# Objectif : process calculateur qui recupere un calcul avec un id de la queue commandes, l'evalue et dépose dans la queue reponse
# Args:   queue commandes, queue reponses 

def calculateur(i, commandes, reponses, verrou):      
    with verrou:
        if not commandes.empty():
            id, commande = commandes.get()
            print("Le calculateur", i, "a récupéré le calcul du demandeur", id, ":", commande)

            # Validation de l'expression
            try:
                reponse = eval(commande)
            except ZeroDivisionError:
                reponse = "erreur: division par zéro"

            reponses.put((id, reponse))
        
if __name__ == "__main__" :
    M = 3   # nombre demandeurs
    N = 6  # nombre de calculteurs

    commandes = mp.Queue() 
    reponses = mp.Queue()       # queue unique de reponse 
    verrou = mp.Lock()

    # generation execution de M processus demandeurs
    liste_demandeur = []    
    for id in range (M) :
        p_demandeur = mp.Process(target = demandeur, args=(id, commandes, reponses))
        p_demandeur.start()
        liste_demandeur.append(p_demandeur)

    # generation execution de N processus calculateurs
    liste_calculateur = []    
    for i in range (N) :
        p_calculateur = mp.Process(target = calculateur, args=(i, commandes, reponses, verrou))
        p_calculateur.start()
        liste_calculateur.append(p_calculateur)

    for p in liste_demandeur:
        p.join()

    for p in liste_calculateur:
        p.join()
        
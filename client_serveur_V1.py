# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : client serveurs
# Date : 20/06/24


import multiprocessing as mp
import os, time, random


#version 1

""" Version 1 : Un demandeur, n calculteurs. (3 points)
Le processus demandeur dépose (par itération) une expression arithmétique à la fois (par exemple
”2 + 3”) dans une file d'attente des demandes (multiprocessing.Queue).
Par ailleurs, chaque processus calculateur récupère une expression, évalue l'expression et dépose
le résultat dans une file d'attente des résultats.
(2) Que faire si l'on doit vérifier la justesse de l'expression. Par exemple, rejeter un expressions telle que ”2 + 3 − ” """


# Objectif : process commande qui genere les N commandes et dépot dans la queue commandes
# Args:   queue commandes, N (int) : nombre de calculs à fournir

def demandeur(commandes, N):        
    for i in range (N) : 
        operateur=random.choice(["+", "-", "*", "/"])   # generation de la commande aléatoire
        opd1 = random.randint(1,10)
        opd2 = random.randint(1,10)
        commande = str(opd1) + operateur + str(opd2)

        commandes.put(commande)     # ajout de la commande demandée par le demmandeur dans la queue
        print("Le demandeur a déposé le calcul", commande)
        time.sleep(1)


# Objectif : process calculateur qui recupere un calcul de la queue commandes et dépot dans la queue reponse
# Args:   queue commandes, queue reponses 

def calculateur(commandes, reponses):        
    commande = commandes.get()     # recuperation du dernier calcul
    print("Le calculateur a récupéré le calcul", commande, end='')
        
    try: # validation de l'expression : la seule erreur est une division par zero
        reponse = eval(commande)
    except ZeroDivisionError:
        reponse = "erreur: division par zéro"

    reponses.put(reponse)       # depot de la reponse dans la queue
    print(", le resultat est :", reponse)



if __name__ == "__main__" :

    N = 5
    commandes = mp.Queue()       # queue stokant les N opérations à effectuer demandées par 1 demandeur
    reponses = mp.Queue()        # queue stokant les resultats par les N calculateurs

    p_demandeur = mp.Process(target = demandeur, args=(commandes, N))
    p_demandeur.start()

    liste_calculateur = []    
    for i in range (N) :
        p_calculateur = mp.Process(target = calculateur, args=(commandes, reponses))
        p_calculateur.start()
        liste_calculateur.append(p_calculateur)

    p_demandeur.join()
    for p in liste_calculateur:
        p.join()
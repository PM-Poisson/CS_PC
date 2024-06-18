# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : estimationd de pi
# Date : 20/06/24

import multiprocessing as mp
import random
import time


""" On peut calculer une valeur approché de PI à l’aide d’un cercle unitaire et la méthode MonteCarlo (MC).
Principe : on échantillonne un point (couple de réels (x, y) ∈ [0.0, 1.0]) qui se situe dans 1 4
du cercle unitaire et on examine la valeur de x2 + y2 ≤ 1 (équation de ce cercle).
➙ Si "vrai", le point est dans le quart du cercle unitaire (on a un hit)
➙ Sinon (cas de miss), .
modifier le code précédent pour effectuer le calcul à l’aide de plusieurs Processus.
☞ Mesurer le temps et comparer.
N.B. : dans la méthode envisagée, on fixe un nombre (p. ex. N = 106
) d’itérations.
Si on décide de faire ce calcul par k processus, chaque processus effectuera N
kitérations. """


# Objectif : calculer le nombre de hits dans un cercle unitaire
# Args:   nb_iteration(int), resultat(queue)

def frequence_de_hits_pour_n_essais(nb_iteration, resultat):
    count = 0
    for _ in range(nb_iteration):
        x = random.random()
        y = random.random()
        # Si le point est dans l’unité circle
        if x * x + y * y <= 1:
            count += 1
    resultat.put(count)

# Objectif : estimation de pi avec calculs en parallele
# Args:   nb_total_iteration(int), k(int) nombre de processus

def calcul(nb_total_iteration, k):
    nb_iteration = nb_total_iteration // k      # nmbr iterations pour chaque processus
    nb_hits_total = 0

    resultat = mp.Queue()
    liste_processus = []

    for i in range(k):                      # creation des k processus
        process = mp.Process(target=frequence_de_hits_pour_n_essais, args=(nb_iteration, resultat))
        process.start()
        liste_processus.append(process)
    
    for p in liste_processus:  
        p.join()
        nb_hits_total += resultat.get()     # somme total des hits par les k processus
    
    pi = 4 * nb_hits_total / nb_total_iteration     # formule de pi à partir des points

    return pi


if __name__ == "__main__":
    
    nb_total_iteration = 10000000  # Nombre d’essais pour l’estimation
    k = 4  # Nombre de processus en parallèle

    start_time = time.time()
    
    pi = calcul(nb_total_iteration, k)
    print("Par la methode multiprocessing, la valeur estimée de Pi est : ", pi)

    end_time = time.time()
    print("Le temps d'exécution est de", end_time - start_time)

    print("Alors qu'avec la première méthode séquentielle, le programme prend en moyenne 2.685 secondes")

# TRACE : Valeur estimée Pi par la méthode Mono−Processus : 3.1412604
# Avec la première méthode séquentielle, le programme prend en moyenne 2.685 secondes
# Alor qu'avec une méthode en parallèle, le pregramme prend entre 0.97 et 1.01 seoonde.
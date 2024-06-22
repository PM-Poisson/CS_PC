import multiprocessing as mp
import time
import random

# Configuration initiale
N = 4  # Nombre de processus
demande_billes = [4, 3, 5, 2]  # Demande de chaque processus
nb_max_billes = 9  # Nombre maximum de billes
m = 5  # Nombre de répétitions de la séquence "demander, utiliser, rendre"

# Initialisation des ressources et des sémaphores
billes_disponibles = mp.Value('i', nb_max_billes)
mutex = mp.Lock()
condition = mp.Condition(mutex)

def demander_billes(pid, k):
    with condition:
        while billes_disponibles.value < k:
            condition.wait()
        billes_disponibles.value -= k
        print(f"Process {pid} a pris {k} billes. Billes restantes: {billes_disponibles.value}")

def rendre_billes(pid, k):
    with condition:
        billes_disponibles.value += k
        print(f"Process {pid} a rendu {k} billes. Billes restantes: {billes_disponibles.value}")
        condition.notify_all()

def processus(pid, k):
    for _ in range(m):
        demander_billes(pid, k)
        # Simuler le travail avec les billes
        time.sleep(random.uniform(0.5, 2.0))
        rendre_billes(pid, k)
        # Simuler le temps entre deux demandes
        time.sleep(random.uniform(0.5, 2.0))

def controleur():
    while True:
        with condition:
            if billes_disponibles.value < 0 or billes_disponibles.value > nb_max_billes:
                print(f"Erreur: Billes disponibles {billes_disponibles.value} en dehors de l'intervalle!")
        time.sleep(1)  # Contrôle périodique

if __name__ == "__main__":
    # Lancer les processus
    processus_list = []
    for i in range(N):
        p = mp.Process(target=processus, args=(i, demande_billes[i]))
        processus_list.append(p)
        p.start()

    # Lancer le processus contrôleur
    controleur_process = mp.Process(target=controleur)
    controleur_process.start()

    # Attendre la fin de tous les processus
    for p in processus_list:
        p.join()

    # Terminer le processus contrôleur
    controleur_process.terminate()
    controleur_process.join()

    print("Tous les processus sont terminés.")
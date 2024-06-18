# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : lecteurs redacteurs
# Date : 20/06/24

import multiprocessing as mp
import time
import random


""" Supposons que pour une simulation, on a n rédacteurs (qui modifient le document) et de m lecteurs de ce document. Le groupe est donc composé de n + m élèves. Par exemple, n = 2 et m = 4.
Un document étant déposé, on ne peut avoir plus d’une rédaction à un moment donné mais il
est possible d’avoir plusieurs lecteurs simultanées (en même temps). Bien entendu, la rédaction
exclue toute lecture et inversement.
Par contre, la priorité est donnée aux rédacteurs. Dès qu’en rédacteur souhaite modifier le document (il manifeste d’abord ce souhait en ajoutant p. ex. +1 sur la variable nb_demande_de_redaction),
plus aucun lecteur supplémentaire ne peut lire le document jusqu’à la fin des rédactions (jusque
nb_demande_de_redaction==0) """



class Document:

    def __init__(self):
        self.nb_demandes_de_redaction = mp.Value('i', 0)
        self.verrou = mp.Lock()
        self.go_lecture = mp.Event()

    # Objectif : demande à commencer la redaction
    # Args:   id (str)
    def commencer_redaction(self,id):
        with self.verrou:
            self.nb_demandes_de_redaction.value += 1
            print("Début de la rédaction de", id)
            time.sleep(1)
            print("Fin de la rédaction de", id)
            self.nb_demandes_de_redaction.value -= 1

            if self.nb_demandes_de_redaction.value == 0:
                self.go_lecture.set()

    # Objectif : demande à commencer la lectire
    # Args:   id (str)
    def commencer_lecture(self, id):
        with self.verrou:
            while self.nb_demandes_de_redaction.value > 0 :
                self.go_lecture.wait()
            print("Début de la lecture de", id)
            time.sleep(1)
            print("Fin de la lecture de", id)
          

if __name__ == "__main__":

    document = Document()
    nb_redacteurs = 2   # n rédacteurs
    nb_lecteurs = 4     # m lecteurs
    
    R1 = mp.Process(target=document.commencer_redaction, args=("R1",))
    R2 = mp.Process(target=document.commencer_redaction, args=("R2",))
    L1 = mp.Process(target=document.commencer_lecture, args=("L1",))
    L2 = mp.Process(target=document.commencer_lecture, args=("L2",))
    L3 = mp.Process(target=document.commencer_lecture, args=("L3",))
    L4 = mp.Process(target=document.commencer_lecture, args=("L4",))
    
    processus = [R1, R2, L1, L2, L3, L4]

    #### SIMULATION

    # Une demande de rédaction (R1) arrive
    # effet de bloquer toutes les demandes de lecture.
    # Puisque pas de rédaction en cours, R1 entre en rédaction
    
    # document.commencer_redaction("R1")
    print("Demande de rédaction (R1)")
    R1.start()

    # Deux demandes de lecture (L1, L2) arrivent
    time.sleep(1)
    print("Demande de lecture (L1)")
    L1.start()

    time.sleep(1)
    print("Demande de lecture (L2)")
    L2.start()
    # Elles sont bloquées jusqu’à la fin de R1
    # R1 termine
    # L1 entre en lecture ; L2 entre en lecture

    # Une demande de rédaction (R2) arrive
    time.sleep(1)
    print("Demande de rédaction (R2)")
    R2.start()

    # Deux demandes de lecture (L3, L4) arrivent mais ces lecteurs ne peuvent pas entrer car R2 a fait une demande.
    time.sleep(1)
    print("Demande de lecture (L3)")
    L3.start()
    time.sleep(1)

    print("Demande de lecture (L4)")
    
    L4.start()

    #Fin de L1 et de L2
    #R2 entre en rédaction
   
    for process in processus:
        process.terminate() 
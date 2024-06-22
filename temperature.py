# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : temperature et pompes
# Date : 20/06/24

import multiprocessing as mp
import random, time


"""  T et P doivent communiquer des données au processus S (screen, affichage), qui affiche différentes mesures à des-
tination d'un utilisateur / opérateur par l'intermédiaire d'un écran d'affichage (le boîtier que l'on retrouve sur le
mur dans un lieu climatisé).
• L'écran d'affichage est une ressource unique et protégée.
Seul le processus S a le droit d'écrire à l'écran
L'objectif global de ce système temps réel embarqué est de maintenir la température et la
pression d'un certain processus chimique dans des limites définies.
 """


class Controleur() : 

    def __init__ (self) :
        self.mem_T = mp.Value('d', 19.0)     # initialise la température de la  piece à 19°
        self.mem_P = mp.Value('d', 1013.0)     # pression initiale en hPa
        self.Seuil_T = 15.0   # parammetre fixe temperature
        self.Seuil_P = 1013.0   # parammetre fixe temperature
        self.message = mp.Queue()   #stocke les messages enregistrés par T et P, les messages sont affichés par S

        self.verrou = mp.Lock()
        self.go_chauffage = mp.Event()
        self.go_pompe = mp.Event()
        
        

    # Objectif : gestionnaire de la temperature (T), toutes les secondes, genere une temperature
    def Capteur_Temp(self) : 
        while True :
            with self.verrou :
                T = random.uniform(max(0,self.mem_T.value - 4), (min(30, self.mem_T.value + 4)))   # generation d'une temperature entre -4° et +4° par rapport à la temp prec pour un aspect plus realiste
                self.mem_T.value = T
            time.sleep(1)

    # Objectif : gestionnaire de la pression (P), toutes les secondes, genere une temperature
    def Capteur_Pression(self) : 
        while True :
            with self.verrou :
                P = random.uniform(max(900, self.mem_P.value - 20), min(1100, self.mem_P.value + 20))
                self.mem_P.value = P
            time.sleep(1)

    # Objectif : gestionnaire du chauffage, s'il recoit l'evenment chauffer, il augmente la temperatuire jusqu'à 19° max 
    def chauffage (self) :
        while True :
            self.go_chauffage.wait()
            if (self.mem_T.value < 19) :       # on fixe la température maximale à 19°C avec un chauffage allumé 
                self.mem_T.value += 1

            message = "Chauffage allumé"    # ajout dans la queue messages à afficher
            self.message.put(message)
            time.sleep(1)

    # Objectif : gestionnaire de la pompe
    def pompe (self) :
        while True :
            self.go_pompe.wait() 
            message = "Pompe ouverte"
            self.message.put(message)
            time.sleep(1)

    # Objectif : gestionnaire controleur : toutes les secondes réveille les systemes de chauffage et seuils si besoin 
    #            et transmet les messages à afficher dans la queue message
    def controleur (self) :
        while True :
            with self.verrou :
                T = self.mem_T.value 
                P = self.mem_P.value 

                if T >= self.Seuil_T :      # selon l'algo qui a été donné
                    self.go_chauffage.clear()
                    if P > self.Seuil_P : 
                        self.go_pompe.set()
                    else :
                        self.go_pompe.clear()
                else: 
                    self.go_pompe.set()
                    self.go_chauffage.set()

                message = "La temperature est de ", T, "°C. Et la pression est de ", P
                self.message.put(message)
            time.sleep(1)

    # Objectif : gestionnaire ecran, toutes les secondes, recupère le dernier message et les affiche
    def ecran (self) :
        while True :       
            message = self.message.get()
            with self.verrou :
                print(message)
                time.sleep(1)



if __name__ == "__main__" :
    
    gestion = Controleur()

    processus = [
        mp.Process(target = gestion.Capteur_Temp),
        mp.Process(target = gestion.Capteur_Pression),
        mp.Process(target = gestion.chauffage),
        mp.Process(target = gestion.pompe),
        mp.Process(target = gestion.controleur),
        mp.Process(target = gestion.ecran),
    ]

    for p in processus :
        p.start()
    
    for p in processus :
        p.join()

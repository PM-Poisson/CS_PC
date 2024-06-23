# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : Jeu de la vie
# Date : 20/06/24

import threading
import time
import os
import random

'''
Le jeu de la Vie (Game of Life) est un automate cellulaire imaginé par John Horton Conway en 1970. 
Malgré des règles très simples, il a été démontré Turing-complet. 

Le jeu de la Vie est un « jeu à zéro joueur », puisqu'il ne nécessite aucune intervention du joueur lors de son déroulement. 
Il s'agit d'un automate cellulaire, un modèle où chaque état conduit mécaniquement à l'état suivant à partir de règles préétablies.
Une cellule possède huit voisines, qui sont les cellules adjacentes horizontalement, verticalement et diagonalement.

À chaque itération, l'état d'une cellule est entièrement déterminé par l'état de ses huit cellules voisines, selon les règles suivantes : 
    Une cellule morte possédant exactement trois cellules voisines vivantes devient vivante (elle naît) ;
    Une cellule vivante possédant deux ou trois cellules voisines vivantes le reste, sinon elle meurt.
'''

# Taille de l'univers (lignes, colonnes)
LIG, COL = 30, 30

# Matrice initiale générée aléatoirement ou initialisée vide (décommenter la version voulue)
mat = [[random.randint(0, 1) for _ in range(COL)] for _ in range(LIG)]
#mat = [[0 for i in range(COL)] for j in range(LIG)]

# Si la matrice initiale est vide, ajouter ici les cases que l'on veut remplir à la main (exemples ci-dessous)
#mat[5][5] = 1
#mat[6][5] = 1
#mat[7][5] = 1

def compter_voisins(mat, x, y):
    '''
    Cette fonction a pour but de compter le nombre de voisins vivants d'une cellule
    
    entrée : coordonnées de la cellule
    sortie : nombre de voisins en vie
    '''
    voisins = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            ni, nj = x + i, y + j
            if 0 <= ni < LIG and 0 <= nj < COL:
                voisins += mat[ni][nj]
    return voisins

def generation(mat, new_mat):
    '''
    Cette fonction a pour but de calculer la génération d'univers suivante
    
    entrée : la matrice atuelle, une nouvelle matrice vide
    sortie : la nouvelle matrice dont la population est générée en fonction de la précédente
    '''
    for i in range(LIG):
        for j in range(COL):
            voisins = compter_voisins(mat, i, j)
            if mat[i][j] == 1 and (voisins < 2 or voisins > 3):
                new_mat[i][j] = 0
            elif mat[i][j] == 0 and voisins == 3:
                new_mat[i][j] = 1
            else:
                new_mat[i][j] = mat[i][j]
    return new_mat

def affichage(mat):
    '''
    Cette fontion gère l'affichage
    
    entrée : matrice de l'univers
    sortie : aucune, affichage sur le terminal
    '''
    os.system('cls' if os.name == 'nt' else 'clear')
    for row in mat:
        print(' '.join(['█' if cell else ' ' for cell in row]))
    print("\n")

def maj():
    '''
    Cette fonction a pour but de faire la mise à jour concurrente à l'aide d'une boucle
    '''
    global mat
    while True:
        new_mat = [[0 for _ in range(COL)] for _ in range(LIG)]
        mat = generation(mat, new_mat)
        time.sleep(0.2)  # Pause de 0.2s entre chaque génération

# Démarre le thread de mise à jour
update_thread = threading.Thread(target=maj)
update_thread.daemon = True
update_thread.start()

# Boucle principale
if __name__ == "__main__":
    try:
        while True:
            affichage(mat)
            time.sleep(0.1)  # Pause de 100ms pour limiter le bug de rafraîchissement
    except KeyboardInterrupt:
        pass
# Authors : Paul-Malo et Estelle ZHENG
# Projet : CS-PC Calculs parallèles
# Title : Course Hippique
# Date : 20/06/24

'''
20 processus sont créés et chaque processus représente un cheval.
Chaque cheval avance aléatoirement sur une ligne qui lui est dédiée. 
On affiche un symbole qui représente le cheval (par exemple "(A>" pour le premier cheval). 
Un cheval affiche son symbole, attend un certain délai aléatoire, 
efface son symbole et le ré-affiche une colonne plus à droite. Ce qui donne l'impression qu'il avance.
Chaque cheval inscrit sa position courante dans une case du tableau partagé. 
Le processus "arbitre" doit à tout moment et en temps réel afficher le cheval qui est en tête de la course. 
'''

import multiprocessing as mp
import time
import random
import sys
import ctypes
import signal

# Quelques codes d'échappement (tous ne sont pas utilisés)
CLEARSCR="\x1B[2J\x1B[;H"          #  Clear SCReen
CLEAREOS = "\x1B[J"                #  Clear End Of Screen
CLEARELN = "\x1B[2K"               #  Clear Entire LiNe
CLEARCUP = "\x1B[1J"               #  Clear Curseur UP
GOTOYX   = "\x1B[%.2d;%.2dH"       #  ('H' ou 'f') : Goto at (y,x), voir le code

DELAFCURSOR = "\x1B[K"             #  effacer après la position du curseur
CRLF  = "\r\n"                     #  Retour à la ligne

# VT100 : Actions sur le curseur
CURSON   = "\x1B[?25h"             #  Curseur visible
CURSOFF  = "\x1B[?25l"             #  Curseur invisible

# VT100 : Actions sur les caractères affichables
NORMAL = "\x1B[0m"                  #  Normal
BOLD = "\x1B[1m"                    #  Gras
UNDERLINE = "\x1B[4m"               #  Souligné


# VT100 : Couleurs : "22" pour normal intensity
CL_BLACK="\033[22;30m"                  #  Noir. NE PAS UTILISER. On verra rien !!
CL_RED="\033[22;31m"                    #  Rouge
CL_GREEN="\033[22;32m"                  #  Vert
CL_BROWN = "\033[22;33m"                #  Brun
CL_BLUE="\033[22;34m"                   #  Bleu
CL_MAGENTA="\033[22;35m"                #  Magenta
CL_CYAN="\033[22;36m"                   #  Cyan
CL_GRAY="\033[22;37m"                   #  Gris

# "01" pour quoi ? (bold ?)
CL_DARKGRAY="\033[01;30m"               #  Gris foncé
CL_LIGHTRED="\033[01;31m"               #  Rouge clair
CL_LIGHTGREEN="\033[01;32m"             #  Vert clair
CL_YELLOW="\033[01;33m"                 #  Jaune
CL_LIGHTBLU= "\033[01;34m"              #  Bleu clair
CL_LIGHTMAGENTA="\033[01;35m"           #  Magenta clair
CL_LIGHTCYAN="\033[01;36m"              #  Cyan clair
CL_WHITE="\033[01;37m"                  #  Blanc

LONGEUR_COURSE = 50 # Tout le monde aura la même copie (donc no need to have a 'value')

# Dessins ASCII pour les chevaux
chevaux_ascii = [
    "   \\   O \n    \\ /|\\\n      / \\",
    "   \\   O \n    \\  |\\\n      / \\",
    "   \\   O \n    \\ /|\n      / \\",
    "   \\   O \n    \\| \\\n      / \\",
    "   \\   O \n    \\|/\n      / \\"
]

#-------------------------------------------------------
# Une liste de couleurs à affecter aléatoirement aux chevaux
lyst_colors=[CL_WHITE, CL_RED, CL_GREEN, CL_BROWN , CL_BLUE, CL_MAGENTA,
             CL_CYAN, CL_GRAY, CL_DARKGRAY, CL_LIGHTRED, CL_LIGHTGREEN,
             CL_LIGHTBLU, CL_YELLOW, CL_LIGHTMAGENTA, CL_LIGHTCYAN]

def effacer_ecran() :
    '''Clear screen'''
    print(CLEARSCR,end='')

def erase_line_from_beg_to_curs() :
    '''Clear progressif de la ligne'''
    print("\033[1K",end='')

def curseur_invisible() :
    '''curseur invisible'''
    print(CURSOFF,end='')

def curseur_visible() :
    '''curseur visible'''
    print(CURSON,end='')

def move_to(lig, col) :
    '''changement de coordonnées'''
    print("\033[" + str(lig) + ";" + str(col) + "f",end='')

def en_couleur(color):
    '''couleur chevaux'''
    print(color,end='')

def en_rouge() :
    '''exemple'''
    print(CL_RED,end='') # Un exemple !

def erase_line():
    '''clear ligne'''
    print(CLEARELN,end='')

# La tache d'un cheval
def un_cheval(ma_ligne : int, keep_running, positions, mutex) : # ma_ligne commence à 0
    '''Fonction d'un cheval'''
    col=1
    while col < LONGEUR_COURSE and keep_running.value :
        with mutex:
            move_to(ma_ligne * 4 + 1, col)  # Ajuster la position en hauteur pour les dessins plus grands
            erase_line()
            en_couleur(lyst_colors[ma_ligne%len(lyst_colors)])
            print(chevaux_ascii[ma_ligne % len(chevaux_ascii)])  # Afficher le dessin ASCII
        col+=1
        positions[ma_ligne] = col
        time.sleep(0.1 * random.randint(1,5))

    # Le premier arrivée gèle la course !
    # J'ai fini, je me dis à tout le monde
    keep_running.value=False

def arbitre(positions, keep_running, mutex):
    '''Fonction arbitre'''
    while keep_running.value:
        time.sleep(0.5)
        max_pos = max(positions)
        min_pos = min(positions)
        leader = -1
        last = -1
        for i in range(len(positions)):
            if positions[i] == max_pos:
                leader = i
            if positions[i] == min_pos:
                last = i
        with mutex:
            move_to(len(positions)*4 + 5, 1)
            erase_line()
            print(f"Premier : {chr(ord('A') + leader)}, Dernier : {chr(ord('A') + last)}")

#------------------------------------------------
def detourner_signal(signum, stack_frame) :
    '''fonction stop'''
    move_to(24, 1)
    erase_line()
    move_to(24, 1)
    curseur_visible()
    print("La course est interrompue ...")
    sys.exit(0)
# ---------------------------------------------------
# La partie principale :
if __name__ == "__main__" :

    import platform
    if platform.system() == "Darwin" :
        mp.set_start_method('fork') # Nécessaire sous macos, OK pour Linux

    keep_running = mp.Value(ctypes.c_bool, True)
    positions = mp.Array('i', [0]*20)
    nbprocess = 20
    mes_process = [0 for i in range(nbprocess)]
    mutex = mp.Lock()

    effacer_ecran()
    curseur_invisible()

    # Détournement d'interruption
    signal.signal(signal.SIGINT, detourner_signal) # CTRL_C_EVENT   ?

    #

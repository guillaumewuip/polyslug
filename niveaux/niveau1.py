#-*- coding: utf-8 -*-

from entites.mur           import Mur
from entites.plateforme    import Plateforme
from entites.obstacleTest  import ObstacleTest
from entites.ennemi1       import Ennemi1
from entites.ennemi2       import Ennemi2
from entites.boss          import Boss
from checkpoint            import Checkpoint

'''
Touts les éléments du niveau
'''

murs = [Mur((0, 400)), Mur((71, 400)), Mur((400, 550))]

plateformes = [Plateforme ((142,450)),Plateforme((142,250))]

obstacles = [ObstacleTest((0,0)), ObstacleTest((100, 0))]

ennemis = [Ennemi1((1000, 200)), Ennemi2((1200, 200))]

boss = Boss((1800, 0))

checkpoints = [
    Checkpoint("red", (200, 530)),
    Checkpoint("blue", (300, 530)),
    Checkpoint("green", (400, 530)),
    Checkpoint("yellow", (500, 530))
]

joueur = (0, 200)


'''
niveau

La structure d'un niveau

@type {Dictionnaire}
'''
niveau = {
    'murs':        murs,
    'obstacles':   obstacles,
    'plateformes': plateformes,
    'ennemis':     ennemis,
    'boss':        boss,
    'checkpoints': checkpoints,
    'joueur':      joueur,
    'taille':      2000   #longueur du niveau en px
}

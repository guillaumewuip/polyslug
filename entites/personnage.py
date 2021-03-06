#-*- coding: utf-8 -*-

import pygame

from entite      import Entite
from lib.sprites import Sprites
from sons import son

'''
collisions

@param  {pygame.sprite.Sprite}  item        Typiquement, le joueur
@param  {Dictionnaire}          niveau
@return {Liste}                             Liste des sprites de Mur et Obstacle en collision avec l'item
'''
def collisions(item, niveau) :
    collisions = []

    for test in ['murs', 'obstacles', 'plateformes'] :
        collisions += pygame.sprite.spritecollide(item, niveau[test], False)

    return collisions


class Personnage(Entite):

    vitesse_x = 0
    vitesse_y = 0
    courir    = False   #True si le joueur cours
    accroupi  = False

    multiCourse = 10     #vitesse de deplacementX (marcher/courir)

    contact_sol = False #utile pour savoir si on peut sauter ou pas

    vie     = 100

    sprites = Sprites('img/p1_spritesheet.png')

    framesGauches = []
    framesDroites = []

    arme = None

    def __init__(self, position) :

        #Découpe des sprites
        self.contruireSprites()

        super(Personnage, self).__init__(position)

    '''
    construireSprites
    '''
    def contruireSprites(self) :

        #images mouvement par défaut
        #(images du joueur)
        images = [
            [(0, 0), (72, 97)],
            [(73, 0), (72, 97)],
            [(146, 0), (72, 97)],
            [(73, 98), (72, 97)],
            [(146, 93), (72, 97)],
            [(219, 0), (72, 97)],
            [(292, 0), (70, 97)],
            [(219, 98), (72, 97)],
            [(365, 0), (72, 97)],
            [(292, 98), (72, 97)],
        ]

        self.framesDroites = self.sprites.sprites(images)
        self.framesGauches = self.sprites.sprites(images, flipX = True)

        self.image = self.imageRepos = self.sprites.sprite((0, 196), (66, 92))

        self.imageAccroupi = [
            self.sprites.sprite((365, 98), (69, 71)),
            self.sprites.sprite((365, 98), (69, 71), flipX = True)
        ]

    '''
    calculY

    Calcul de la position verticale
    Avec gestion des collisions bords, des collisions murs

    @param {dic}    niveau      L'état du niveau
    '''
    def calcul_Y(self, niveau) :

        #Calcul vitesse verticale due à la gravité
        if self.rect.bottom < niveau['height']:
            if self.vitesse_y == 0 :
                self.vitesse_y = 1
            else:
                self.vitesse_y += 0.35 #PFD

        #finalement, on ne stope pas le joueur au contact du bas de la fenêtre
        #if self.rect.bottom >= niveau['height']:
        #    if self.vitesse_y > 0 :   # on ne peut pas descendre plus bas
        #        self.vitesse_y = 0

        #    #self.rect.y = niveau['height'] - self.rect.height #on force à ne pas dépasser le sol
        #    self.rect.bottom = niveau['height']
        #    self.contact_sol = True

        #Si on touche le bas de la fenêtre
        if self.rect.bottom >= niveau['height']:
            self.vitesse_y = self.vitesse_y/5 + 1 #on reduit pour faire comme si on coulait
        if self.rect.bottom >= (niveau['height']+ 100):
            self.blessure(1000)#l'entite meurt

        self.rect.y += self.vitesse_y

        #si on touche quelque chose en chemin
        for collision in collisions(self, niveau) :

            if self.vitesse_y > 0 : #si on se déplace en bas, on force le contact avec le haut

                #pour les elements qui ne sont pas des plateformes
                #ou les plateformes si on est au dessus (on peut monter par dessous)
                if (collision.plateforme == False
                    or (collision.plateforme == True and self.rect.bottom <= collision.rect.bottom)) :
                    self.rect.bottom = collision.rect.top
                    self.contact_sol = True
                    self.vitesse_y = 0 #on prend en compte la vitesse 0 pour calcul gravité

            if self.vitesse_y < 0 : #si on se déplace vers le haut, on force le contact avec le bas

                #si c'est une plateforme on passe a travers, ie on change rien
                if collision.plateforme == False :
                    self.rect.top = collision.rect.bottom
                    self.vitesse_y = 0 #on prend en compte la vitesse 0 pour calcul gravité

                self.contact_sol = False



    '''
    calculX

    Calcul de la position horizontale
    Avec gestion des collisions bords, des collisions murs et de l'accroupissement
    Et calcul de l'image courante

    @param {dic}    niveau      L'état du niveau
    '''
    def calcul_X(self, niveau) :

        #si on touche un bord du niveau
        if (self.rect.x < 0 and self.vitesse_x < 0) \
            or (self.rect.x + self.rect.width > niveau['width'] and self.vitesse_x > 0):
            self.vitesse_x = 0

        #si on est accroupi, on ne peut plus bouger
        if not self.accroupi :
            self.rect.x += self.vitesse_x * self.multiCourse # * multi pour fluidité du jeu

        #si on touche quelque chose en chemin
        for collision in collisions(self, niveau) :
            if self.vitesse_x > 0 : #si on se déplace à droite, on force le contact avec le côté gauche
                if collision.plateforme == False:# pour les plateformes on ne le fait pas
                    self.rect.right = collision.rect.left
            if self.vitesse_x < 0 : #si on se déplace à gauche, on force le côté droit
                if collision.plateforme == False:# pour les plateformes on ne le fait pas
                    self.rect.left = collision.rect.right
            #on ne force pas la vitesse_x à 0 si jamais l'obstacle disparaît de lui même
            #pas besoin de relancer le keydown clavier

        #Gestion de l'image
        #on prend soin de regarder dans la bonne direction
        if self.vitesse_x > 0 : #image si déplacement vers la droite
            if self.accroupi :
                self.image = self.imageAccroupi[0]
            else :
                self.image = self.framesDroites[(self.rect.x // 30) % len(self.framesDroites)]
        elif self.vitesse_x < 0 : #image si déplacement vers la gauche
            if self.accroupi :
                self.image = self.imageAccroupi[1]
            else :
                self.image = self.framesGauches[(self.rect.x // 30) % len(self.framesGauches)]
        else : #image si perso à l'arrêt
            if self.accroupi :
                self.image = self.imageAccroupi[0]
            else :
                self.image = self.imageRepos

    '''
    positionMain

    @return {tup}   La position de la main
    '''
    def positionMain(self) :

        position = self.position()

        main = [0, 0]
        main[0], main[1] = position[0], position[1]
        main[1] += 70 if not self.accroupi else 50
        main[0] += 6

        return main

    '''
    update

    Calcul de la position du joueur

    @param {dic}    niveau      l'état du niveau
    '''
    def update(self, niveau, *args) :

        self.calcul_X(niveau)
        self.calcul_Y(niveau)

        self.arme.position(self.positionMain())

    '''
    deplacementX

    @param {int : 1 | -1}    vitesse     Vitesse de déplacement.
                                         1 : déplacement vers la droite
                                        -1 : vers la gauche
    '''
    def deplacementX(self, vitesse) :
        self.vitesse_x = vitesse

    '''
    vitesseCourse

    Switch entre marche/course

    @param {Boolean}    courir      True : on court
    '''
    def vitesseCourse(self, courir) :

        self.courir = courir
        self.multiCourse = 6 if not self.courir else 12

    '''
    seBaisser

    Le joueur s'accroupi, son rect retrécie en hauteur
    On ne peut plus bouger une fois accroupi

    @param {Boolean}    accroupi    True : joueur accroupi
    '''
    def seBaisser(self, accroupi) :
        self.accroupi = accroupi

        #le rect accroupi est plus petit en hauteur de 21 px
        if self.accroupi :
            self.rect.y += 21
            self.rect.height -= 21
        else :
            self.rect.y -= 21
            self.rect.height += 21

    '''
    sauter
    '''
    def sauter(self) :
        if self.contact_sol : #on ne peut pas sauter que si on est en contact avec le sol
            self.vitesse_y = -10
            self.contact_sol = False
            son.sonSaut()

    '''
    blessure

    Supprimer l'arme des groupes auxquels elle appartient
    Jouer son
    Appeler super

    @param {int}    vie
    '''
    def blessure(self, vie):
        super(Personnage, self).blessure(vie)
        if self.vie <= 0 :
            self.arme.kill()
            son.sonMort()

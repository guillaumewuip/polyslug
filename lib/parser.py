#-*- codind: utf-8 -*-

import json
import importlib


groupes  = {
    'ennemis'     : ['Ennemi1', 'Ennemi2'], #  , 'Ennemi3', 'Ennemi4'],
    'murs'        : ['Mur', 'Plateforme'],
    'obstacles'   : ['Obstacles'],
    'checkpoints' : ['Checkpoint'],
    'joueur'      : ['Joueur'],
}

dynamiques = ['ennemis', 'checkpoints', 'joueur', 'checkpoints']


def groupe(classe) :

    for k, v in groupes.items() :
        if classe in v :
            return k

    return None


def constructionTiles(data) :

    tiles = {}

    for tileset in data['tilesets'] :

        setId = tileset['firstgid']

        image = 'img/' + tileset['name'] + '.png'

        tileHeight = tileset['tileheight']
        tileWidth  = tileset['tilewidth']

        gridWidth  = tileset['imagewidth'] / tileWidth
        gridHeight = tileset['imageheight'] / tileHeight
        grid       = gridWidth * gridHeight

        if 'tileproperties' in tileset :
            for t, val in tileset['tileproperties'].items() :
                id = setId + int(t)

                i = int(t) % gridWidth
                j = int(t) // gridHeight

                print(t, i, j)

                if 'class' in val :
                    classe = val['class']
                else :
                    classe = None

                tiles[id] = {
                    'image' : image,
                    'rect'  : {
                        'x'     : j * tileWidth,
                        'y'     : i * tileHeight,
                        'width' : tileWidth,
                        'height': tileHeight
                        },
                    'classe' : classe,
                    'groupe' : groupe(classe)
                }

    with open('lib/data.json', 'w') as outfile:
        json.dump(tiles, outfile)

    return tiles


def recupererCalquePrincipal(data) :

    for l in data['layers'] :
        if l['name'] in ['Principal', 'principal'] :
            return l

def importClass(groupe, classe):

    if groupe not in ['ennemis', 'obstacles', 'murs', 'joueur'] :
        module = importlib.import_module(classe.lower())
    else :
        module = importlib.import_module('entites.' + classe.lower())

    return getattr(module, classe)


def construction(calque, tiles):

    niveau = {
        'murs':        [],
        'obstacles':   [],
        'plateformes': [],
        'ennemis':     [],
        'boss':        [],
        'checkpoints': [],
        'joueur':      [],
        'taille':      0   #longueur du niveau en px
    }

    layerWidth  = calque['width']
    layerHeight = calque['height']

    for index, item in enumerate(calque['data']) :

        if item != 0 and item in tiles:

            tile   = tiles[item]
            groupe = tile['groupe']
            classe = tile['classe']

            i = index % layerWidth
            j = index // layerHeight

            print(groupe, classe)

            if groupe in niveau :

                if groupe in dynamiques :
                    instance = importClass(groupe, classe)((i,j))
                else :
                    instance = importClass(groupe, classe)((i,j), tile['image'], tile['rect'])

                print(item)
                niveau[groupe].append(item)

    return niveau


def genererNiveau(fichier) :

    contenu = open(fichier, 'r' ).read()

    data = json.loads(contenu)

    tiles = constructionTiles(data)

    principal = recupererCalquePrincipal(data)

    if not principal :
        print("Pas de calque principal")
    else :
        niveau = construction(principal, tiles)
        print niveau


#genererNiveau('lib/test.json')
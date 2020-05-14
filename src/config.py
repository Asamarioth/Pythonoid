FPS = 60
WINDOWWIDTH = 1280
WINDOWHEIGHT = 720

BLOCKWIDTH = 50
BLOCKHEIGHT = 25
BALLSIZE = 25
BALLSPEED = 10  # bazowa prędkość piłki o którą oparte są obliczenia
PLAYERWIDTH = 100
PLAYERHEIGHT = 15
PLAYERMOVEMENT = 10  # Ile pikseli porusza się paletka gracza
SCORE = 0
LIFES = 13
MAXLVL = 3
GAMESTATE = 0  # 0 - gra trwa, 1 - ukończono poziom, 2 - porażka
# KOLORY
GRAY = (100, 100, 100)
NAVYBLUE = (60, 60, 100)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 128, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
BLACK = (0, 0, 0)


def score_change(reset=False, x=0):
    global SCORE
    if reset:
        SCORE = 0
    else:
        SCORE += x


def get_score():
    return SCORE


def life_change(x):
    global LIFES
    LIFES += x


def get_lifes():
    return LIFES


def gamestate_change(x):
    global GAMESTATE
    GAMESTATE = x


def get_gamestate():
    return GAMESTATE


def get_playermovement():
    return PLAYERMOVEMENT


def change_playermovement(x):
    global PLAYERMOVEMENT
    PLAYERMOVEMENT += x

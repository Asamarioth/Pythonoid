import pygame
import sys
from src.objects import *
from src.config import *
from src.pygame_textinput import TextInput
from pygame.locals import *
import os
import time


def text_objects(text, font, colour):
    textsurface = font.render(text, True, colour)
    return textsurface, textsurface.get_rect()


def load_img(img_path):
    img_path = os.path.join('img', img_path)
    image = pygame.image.load(img_path).convert_alpha()
    return image


def load_level(file_path, level_number):  # funkcja wczytuje z pliku dane poziomu i zwraca je jako słownik
    file_path = os.path.join('levels', file_path)
    level = {}
    file = open(file_path)
    while_cond = True
    skip_line = 0
    level_reading = 0
    it = 0

    while while_cond:
        for x in file:
            # pomijanie czytania linii jeśli jest ona komentarzem, pusta, bądź podniesiona jest flaga pomijania
            if x[0] == "]":
                if level_reading == 1:
                    level_reading = 0
                elif skip_line == 1:
                    skip_line = 0
            elif x[0] == "#" or x[0] == "\n" or skip_line == 1:
                continue
            elif x[0] == "[":
                if int(x[1]) == level_number:
                    level_reading = 1
                else:
                    skip_line = 1
            else:
                level[it] = x[:len(x) - 1]  # unika dodawania znaku nowej linii do słownika
                it += 1
            while_cond = False
    file.close()
    return level


def draw_level(level, img_set, all_sprites_list, brick_sprites_list):
    for x in range(len(level)):
        for y in range(len(level[x])):
            if level[x][y] == "1":
                if x % 3 == 0 or x % 3 == 1:
                    brick = Brick(load_img(img_set[0]), BLOCKWIDTH, BLOCKHEIGHT, "sfx/bee2.ogg")
                elif x % 3 == 2:
                    brick = Brick(load_img(img_set[1]), BLOCKWIDTH, BLOCKHEIGHT, "sfx/bee2.ogg")
                brick.rect.x = 15 + y * BLOCKWIDTH / 2
                brick.rect.y = (2 + x) * BLOCKHEIGHT
            else:
                continue
            all_sprites_list.add(brick)
            brick_sprites_list.add(brick)


def read_score(file_path):
    file = open(file_path)
    lista = list()
    dicto = {}
    temp2 = 0
    for x in file:
        temp1 = ""
        if x[0] == "\n":
            continue
        else:
            it = 0
            while x[it] != "-":
                temp1 += x[it]
                it += 1
            it += 1
            temp2 = int(x[it:])
            dicto["p"] = temp1
            dicto["s"] = temp2
            lista.append(dicto.copy())
            dicto.clear()
    file.close()
    return lista


def write_score(scr):
    def temp_sort(x):
        return x["s"]

    lista = read_score("score.txt")
    if scr["s"] > int(lista[len(lista) - 1]["s"]):
        lista.pop(len(lista) - 1)
        lista.append(scr)
        lista.sort(reverse=True, key=temp_sort)
    else:
        return

    file = open("score.txt", "w")
    for x in lista:
        file.write(x['p'] + "-" + str(x['s']) + "\n")
    file.close()


def spawn_bonus(img_set, all_sprites, paddle, ball):
    temp = random.randint(0, 7)
    bonus = Bonus(load_img(img_set[temp]), BALLSIZE, BALLSIZE, paddle, ball, temp)
    all_sprites.add(bonus)
    return bonus.prize


def reset_bonus_effects(player, ball, current_bonus, player_img, ball_img):
    if player.bonus_active:
        if current_bonus == 0:
            change_playermovement(-5)
        elif current_bonus == 1:
            player.image = load_img(player_img[0])
            player.resize(-50, 0)
        elif current_bonus == 2:
            player.image = load_img(player_img[0])
            player.resize(25, 0)
        elif current_bonus == 3:
            ball.speed -= 2
        elif current_bonus == 4:
            ball.speed += 2
        elif current_bonus == 5:
            ball.image = load_img(ball_img[1])
            ball.resize(-5, -5)
        elif current_bonus == 6:
            ball.image = load_img(ball_img[1])
            ball.resize(5, 5)
        elif current_bonus == 7:
            ball.passthrough = False
        player.bonus_active = False


# tekst, topleft x, topleft y, szerokośc, wysokość, obrazek, funkcja po kliknięciu
def button(msg, x, y, w, h, img, fun=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    bg = Background(load_img(img), w, h)
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        bg.resize(w + 10, h)
        displaysurf.blit(bg.image, (x - 5, y))
        if click[0] == 1 and fun is not None:
            fun()
    else:
        displaysurf.blit(bg.image, (x, y))

    smalltext = pygame.font.Font("freesansbold.ttf", 20)
    textsurf, textrect = text_objects(msg, smalltext, BLACK)
    textrect.center = ((x + (w / 2)), (y + (h / 2)))
    displaysurf.blit(textsurf, textrect)


def main():
    pygame.mixer.pre_init(buffer=256)
    pygame.init()
    pygame.mixer.init()
    global fpsclock, displaysurf
    pygame.display.set_caption("Arkanoid")
    fpsclock = pygame.time.Clock()
    displaysurf = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.font.init()
    menu()


def menu():
    in_menu = True
    bg = Background(load_img("background_menu.png"), WINDOWWIDTH, WINDOWHEIGHT)
    while in_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        displaysurf.blit(bg.image, (0, 0))
        button("Start", WINDOWWIDTH / 2 - 100, 50, 100, 50, "button1.png", game_loop)
        button("Score", WINDOWWIDTH / 2 - 100, 125, 100, 50, "button1.png", scoreboard)
        button("Quit", WINDOWWIDTH / 2 - 100, 200, 100, 50, "button1.png", sys.exit)
        pygame.display.update()
        fpsclock.tick(10)


def scoreboard():
    fonts = pygame.font.Font("freesansbold.ttf", 25)
    test = read_score("score.txt")

    bg = Background(load_img("background_menu.png"), WINDOWWIDTH, WINDOWHEIGHT)
    displaysurf.blit(bg.image, (0, 0))

    i = 1
    for x in test:
        text = x['p'] + " - " + str(x['s'])
        textsurf, textrect = text_objects(text, fonts, BLACK)
        textrect.center = (WINDOWWIDTH / 2, i * 60)
        displaysurf.blit(textsurf, textrect)
        i += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    menu()
        button("Menu", 50, WINDOWHEIGHT - 50, 100, 50, "button1.png", menu)
        pygame.display.update()
        fpsclock.tick(15)


def paused():
    pause = True
    text = pygame.font.Font("freesansbold.ttf", 20)
    textsurf, textrect = text_objects("Spacja aby kontynuować, Esc aby wyjść do menu", text, BLACK)
    textrect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
    bg = Background(load_img("button1.png"), 600, 150)
    displaysurf.blit(bg.image, (340, WINDOWHEIGHT / 2 - 75))
    displaysurf.blit(textsurf, textrect)
    while pause:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    menu()

        pygame.display.update()
        fpsclock.tick(15)


def end_screen(victory):
    text = pygame.font.Font("freesansbold.ttf", 20)
    bg = Background(load_img("button1.png"), 600, 150)
    textsurf, textrect = text_objects("Wpisz swoje imię (Enter aby zatwierdzić)", text, BLACK)
    textrect.center = (640, WINDOWHEIGHT / 2 - 40)
    wynik = {}
    name = TextInput()

    while True:
        events = pygame.event.get()
        displaysurf.blit(bg.image, (340, WINDOWHEIGHT / 2 - 75))
        displaysurf.blit(textsurf, textrect)
        rect = Rect(440, WINDOWHEIGHT / 2 - 0, 400, 30)
        pygame.draw.rect(displaysurf, WHITE, rect)
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if (name.update(events)) is True:
            wynik = {"p": name.get_text(), "s": int(get_score())}
            write_score(wynik)
            menu()
        displaysurf.blit(name.get_surface(), (440, WINDOWHEIGHT / 2 - 0))
        pygame.display.update()
        fpsclock.tick(15)


def game_loop():
    myfont = pygame.font.SysFont('Times New Roman', 30)

    lvlnumber = 1

    ball_img = [
        "ball.png",
        "ball2.png",
        "ball3.png",
        "ball4.png",
        "ball5.png",
        "ball6.png",
        "ball7.png",
        "ball8.png"
    ]
    player_img = [
        "player1.png"
    ]
    brick_img = [
        "block1.png",
        "block2.png",
        "block3.png",
        "block4.png",
        "block5.png",
        "block6.png"
    ]
    background_img = [
        "background_game.png"
    ]
    background = Background(load_img(background_img[0]), WINDOWWIDTH, WINDOWHEIGHT)
    scoreboard_bg = Background(load_img("back1.png"), WINDOWWIDTH, 50)
    all_sprites_list = pygame.sprite.Group()
    all_bricks = pygame.sprite.Group()

    level = load_level("levels.txt", lvlnumber)
    draw_level(level, brick_img, all_sprites_list, all_bricks)

    player = Player(load_img(player_img[0]), PLAYERWIDTH, PLAYERHEIGHT)
    ball = Ball(load_img(ball_img[1]), BALLSIZE, BALLSIZE, player, all_bricks,
                ["sfx/gravity_on.ogg", "sfx/castanets.ogg"])

    all_sprites_list.add(player)
    all_sprites_list.add(ball)
    bonus_event = pygame.USEREVENT + 1
    pygame.time.set_timer(bonus_event, 5000)
    current_bonus = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == bonus_event:
                reset_bonus_effects(player, ball, current_bonus, player_img, ball_img)
                current_bonus = spawn_bonus(ball_img, all_sprites_list, player, ball)
                bonus_delay = random.randint(10000, 15000)
                pygame.time.set_timer(bonus_event, bonus_delay)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    paused()
                if event.key == pygame.K_ESCAPE:
                    score_change(True)
                    menu()
                if event.key == pygame.K_F1:
                    for x in all_bricks:
                        x.kill()

        keys = pygame.key.get_pressed()
        player.velocity = 0
        if keys[pygame.K_LEFT]:
            player.move_left(-get_playermovement())
        if keys[pygame.K_RIGHT]:
            player.move_right(get_playermovement())

        all_sprites_list.update()
        displaysurf.blit(scoreboard_bg.image, (0, 0))
        displaysurf.blit(background.image, (0, 50))
        textsurface = myfont.render("Punkty:" + str(get_score()), False, BLACK)
        displaysurf.blit(textsurface, (10, 10))
        textsurface = myfont.render("Życia:" + str(get_lifes()), False, BLACK)
        displaysurf.blit(textsurface, (WINDOWWIDTH - 110, 10))
        textsurface = myfont.render("Poziom:" + str(lvlnumber), False, BLACK)
        displaysurf.blit(textsurface, (WINDOWWIDTH / 2 - 50, 10))
        all_sprites_list.draw(displaysurf)
        pygame.display.update()

        if len(all_bricks) == 0:
            gamestate_change(1)
        if get_gamestate() == 1:
            lvlnumber += 1
            if lvlnumber <= MAXLVL:
                level = load_level("levels.txt", lvlnumber)
                time.sleep(0.5)
                draw_level(level, brick_img, all_sprites_list, all_bricks)
                player.reset()
                ball.update = ball.start
                gamestate_change(0)
            else:
                end_screen(True)
        elif get_gamestate() == 2:
            end_screen(False)
        fpsclock.tick(FPS)


if __name__ == '__main__':
    main()

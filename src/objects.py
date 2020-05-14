import pygame
from src.config import *
import math
import random

random.seed


class Player(pygame.sprite.Sprite):
    def __init__(self, image, width, height):
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT - height / 2))
        self.velocity = 0
        self.bonus_active = False

    def move_left(self, pixels):
        self.velocity = pixels
        self.rect.x += self.velocity
        # Check that you are not going too far (off the screen)
        if self.rect.x < 0:
            self.rect.x = 0

    def move_right(self, pixels):
        self.velocity = pixels
        self.rect.x += self.velocity
        # Check that you are not going too far (off the screen)
        if self.rect.x > WINDOWWIDTH - self.rect.width:
            self.rect.x = WINDOWWIDTH - self.rect.width

    def reset(self):
        self.rect = self.image.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT - PLAYERHEIGHT / 2))
        self.velocity = 0

    def resize(self, width, height):
        self.rect.width = self.rect.width + width
        self.rect.height = self.rect.height + height
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))


class Ball(pygame.sprite.Sprite):
    speed = BALLSPEED
    anglel = 45
    angleh = 135

    def __init__(self, image, width, height, paddle, bricks, sound):
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(WINDOWWIDTH / 2, WINDOWHEIGHT / 2))
        self.paddle = paddle
        self.bricks = bricks
        self.update = self.start
        self.fpx = self.rect.centerx
        self.fpy = self.rect.centery
        self.fpdx = 0
        self.fpdy = 1
        self.passthrough = False
        self.sound_bounce = pygame.mixer.Sound(sound[0])
        self.sound_death = pygame.mixer.Sound(sound[1])

    def resize(self, width, height):
        self.rect.width = self.rect.width + width
        self.rect.height = self.rect.height + height
        self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))

    def start(self):
        self.rect.centerx = self.paddle.rect.centerx
        self.rect.bottom = self.paddle.rect.top
        if pygame.mouse.get_pressed()[0] == 1:
            self.fpx = self.rect.centerx
            self.fpy = self.rect.centery
            self.fpdx = 0
            self.fpdy = 1
            self.update = self.move

    def setfp(self):
        """use whenever usual integer rect values are adjusted"""
        self.fpx = self.rect.centerx
        self.fpy = self.rect.centery

    def setint(self):
        """use whenever floating point rect values are adjusted"""
        self.rect.centerx = self.fpx
        self.rect.centery = self.fpy

    def move(self):
        # odbicie od paletki
        if self.rect.colliderect(self.paddle.rect) and self.fpdy > 0:
            ballpos = self.rect.width + self.rect.left - self.paddle.rect.left - 1
            ballmax = self.rect.width + self.paddle.rect.width - 2
            factor = float(ballpos) / ballmax
            angle = math.radians(self.angleh - factor * (self.angleh - self.anglel))
            self.fpdx = self.speed * math.cos(angle)
            self.fpdy = -self.speed * math.sin(angle)
            pygame.mixer.Channel(0).play(self.sound_bounce)

        self.fpx = self.fpx + self.fpdx
        self.fpy = self.fpy + self.fpdy
        self.setint()

        # sprawdzenie czy piłka nie dotarła do krawędzi planszy
        if self.rect.left < 0:
            self.rect.left = 0
            self.setfp()
            self.fpdx = -self.fpdx
            pygame.mixer.Sound.play(self.sound_bounce, maxtime=100)
        if self.rect.right > WINDOWWIDTH:
            self.rect.right = WINDOWWIDTH
            self.setfp()
            self.fpdx = -self.fpdx
            pygame.mixer.Sound.play(self.sound_bounce, maxtime=100)
        if self.rect.top < 50:
            self.rect.top = 50
            self.setfp()
            self.fpdy = -self.fpdy
            pygame.mixer.Sound.play(self.sound_bounce, maxtime=100)
        if self.rect.bottom > WINDOWHEIGHT:
            pygame.mixer.Sound.play(self.sound_death, maxtime=100)
            #pygame.mixer.Channel(1).play(self.sound_death)
            self.update = self.start
            life_change(-1)
            if get_lifes() <= 0:
                gamestate_change(2)

        # zderzenie piłki z blokami
        brickscollided = pygame.sprite.spritecollide(self, self.bricks, False)
        if brickscollided:
            oldrect = self.rect
            left = right = up = down = 0

            for brick in brickscollided:
                # [] - brick, () - ball
                if not self.passthrough:
                    # ([)]
                    if oldrect.left < brick.rect.left < oldrect.right < brick.rect.right:
                        self.rect.right = brick.rect.left
                        self.setint()
                        left = -1

                    # [(])
                    if brick.rect.left < oldrect.left < brick.rect.right < oldrect.right:
                        self.rect.left = brick.rect.right
                        self.setint()
                        right = 1

                    # top ([)] bottom
                    if oldrect.top < brick.rect.top < oldrect.bottom < brick.rect.bottom:
                        self.rect.bottom = brick.rect.top
                        self.setint()
                        up = -1

                    # top [(]) bottom
                    if brick.rect.top < oldrect.top < brick.rect.bottom < oldrect.bottom:
                        self.rect.top = brick.rect.bottom
                        self.setint()
                        down = 1

                brick.kill()
                pygame.mixer.Sound.play(brick.sound,maxtime=150)
                #pygame.mixer.Channel(2).play(brick.sound)
                score_change(False, 10)
            # odbicie
            if left + right != 0:
                self.fpdx = (left + right) * abs(self.fpdx)
            if up + down != 0:
                self.fpdy = (up + down) * abs(self.fpdy)


class Brick(pygame.sprite.Sprite):
    def __init__(self, image, width, height, sound):
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()
        self.velocity = 0
        self.sound = pygame.mixer.Sound(sound)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, image, width, height, paddle, ball, prize):
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(0 + random.randint(50, WINDOWWIDTH - 50), 50 + height / 2))
        self.paddle = paddle
        self.prize = prize
        self.ball = ball

    def update(self):
        if self.rect.colliderect(self.paddle.rect):
            self.reward()
            self.kill()
        self.rect.y += 4
        if self.rect.bottom > WINDOWHEIGHT:
            self.kill()

    def reward(self):
        self.paddle.bonus_active = True
        if self.prize == 0:
            change_playermovement(5)
        elif self.prize == 1:
            self.paddle.resize(50, 0)
        elif self.prize == 2:
            self.paddle.resize(-25, 0)
        elif self.prize == 3:
            self.ball.speed += 2
        elif self.prize == 4:
            self.ball.speed -= 2
        elif self.prize == 5:
            self.ball.resize(5, 5)
        elif self.prize == 6:
            self.ball.resize(-5, -5)
        elif self.prize == 7:
            self.ball.passthrough = True


class Background(pygame.sprite.Sprite):
    def __init__(self, image, width, height):
        super().__init__()
        self.image = image
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

    def resize(self, width, height):
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

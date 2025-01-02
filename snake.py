import math
import random
import pygame
import random
import tkinter as tk
from tkinter import messagebox

width = 500
height = 500
cols = 25
rows = 20


class cube():
    rows = 20
    w = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 0, 0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        x, y = self.pos
        self.pos = (x + self.dirnx, y + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class snake():
    body = []
    turns = {}

    def __init__(self, color, pos):
        self.color = color
        self.head = cube(pos)
        self.body = [self.head]
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            keys = pygame.key.get_pressed()

            if keys[pygame.K_LEFT]:
                self.dirnx = -1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            elif keys[pygame.K_RIGHT]:
                self.dirnx = 1
                self.dirny = 0
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            elif keys[pygame.K_UP]:
                self.dirnx = 0
                self.dirny = -1
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]
            elif keys[pygame.K_DOWN]:
                self.dirnx = 0
                self.dirny = 1
                self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                c.move(c.dirnx, c.dirny)

    def reset(self, pos):
        self.head = cube(pos)
        self.body = [self.head]
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0] - 1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0] + 1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0], tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0], tail.pos[1] + 1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i == 0:
                c.draw(surface, True)
            else:
                c.draw(surface)


def drawGrid(w, rows, surface):
    sizeBtwn = w // rows
    x = 0
    y = 0
    for l in range(rows):
        x += sizeBtwn
        y += sizeBtwn
        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, w))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (w, y))


def randomSnack(rows, snake_obj, obstacles_positions=None):
    """
    Генерирует позицию для еды, не совпадающую
    с позициями тела змейки и препятствий (если заданы).
    """
    if obstacles_positions is None:
        obstacles_positions = []

    occupied = set([c.pos for c in snake_obj.body] + obstacles_positions)

    while True:
        x = random.randrange(0, rows)
        y = random.randrange(0, rows)
        if (x, y) not in occupied:
            return (x, y)


def createObstacles(rows, snake_obj, count=5):
    """
    Генерируем список кубиков-препятствий (obstacles).
    count — сколько препятствий хотим расставить.
    """
    obstacles_list = []
    occupied = set([c.pos for c in snake_obj.body])

    i = 0
    while i < count:
        x = random.randrange(0, rows)
        y = random.randrange(0, rows)
        if (x, y) not in occupied and all(obs.pos != (x, y) for obs in obstacles_list):
            obstacles_list.append(cube((x, y), dirnx=0, dirny=0, color=(128, 128, 128)))
            i += 1
    return obstacles_list


def redrawWindow(win, s, snack, bonus_snack, obstacles):
    win.fill((0, 0, 0))
    drawGrid(width, rows, win)

    snack.draw(win)

    if bonus_snack:
        bonus_snack.draw(win)


    for obs in obstacles:
        obs.draw(win)

    s.draw(win)

    pygame.display.update()


def main():
    global width, rows
    pygame.init()
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Snake with obstacles, bonus food, and wrap-around")

    s = snake((255, 0, 0), (10, 10))
    s.addCube()

    obstacles = createObstacles(rows, s, count=5)

    snack = cube(randomSnack(rows, s, [obs.pos for obs in obstacles]), color=(0, 255, 0))

    bonus_snack = None
    bonus_snack_timer = 0
    BONUS_TIME = 300
    BONUS_PROBABILITY = 0.01

    clock = pygame.time.Clock()
    running = True

    while running:
        pygame.time.delay(50)
        clock.tick(10)
        s.move()

        headX, headY = s.head.pos
        if headX >= rows:
            headX = 0
        elif headX < 0:
            headX = rows - 1

        if headY >= rows:
            headY = 0
        elif headY < 0:
            headY = rows - 1

        s.head.pos = (headX, headY)
        s.body[0].pos = s.head.pos

        for obs in obstacles:
            if s.head.pos == obs.pos:
                print("Score:", len(s.body))
                s.reset((10, 10))
                obstacles = createObstacles(rows, s, count=5)
                snack = cube(randomSnack(rows, s, [obs.pos for obs in obstacles]), color=(0, 255, 0))
                bonus_snack = None
                bonus_snack_timer = 0
                break

        if s.head.pos == snack.pos:
            s.addCube()
            snack = cube(randomSnack(rows, s, [obs.pos for obs in obstacles]), color=(0, 255, 0))

        if bonus_snack and s.head.pos == bonus_snack.pos:
            for _ in range(3):
                s.addCube()
            bonus_snack = None
            bonus_snack_timer = 0

        for x in range(len(s.body)):
            if s.body[x].pos in list(map(lambda z: z.pos, s.body[x + 1:])):
                print("Score:", len(s.body))
                s.reset((10, 10))
                obstacles = createObstacles(rows, s, count=5)
                snack = cube(randomSnack(rows, s, [obs.pos for obs in obstacles]), color=(0, 255, 0))
                bonus_snack = None
                bonus_snack_timer = 0
                break

        if bonus_snack:
            bonus_snack_timer -= 1
            if bonus_snack_timer <= 0:
                bonus_snack = None
        else:
            if random.random() < BONUS_PROBABILITY:
                bonus_snack = cube(randomSnack(rows, s, [obs.pos for obs in obstacles]), color=(255, 255, 0))
                bonus_snack_timer = BONUS_TIME

        redrawWindow(win, s, snack, bonus_snack, obstacles)

    pass


if __name__ == "__main__":
    main()
